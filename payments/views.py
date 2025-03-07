from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from payments.models import Payment
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from admin_user.jwtAuthentication import CustomJWTAuthentication , CustomAdminJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from json import loads
from packages.models import BookedPackage
from resorts.models import BookedResort
from flights.models import BookedFlight
from visas.models import VisaBooked
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django_redis import get_redis_connection
from datetime import date
from datetime import timedelta

redis_conn = get_redis_connection('default')


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

class CreateCheckoutSessionView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        
        try:
            data = request.data
            amount = data.get("amount", 0)
            name = data.get("name") 
            booked_id = data.get("booked_id")
            category = data.get("category")

            print("Received data:", data)

            amount = float(amount)

            # Validate input
            if not amount or amount <= 0:
                return JsonResponse({"error": "Invalid amount"}, status=400)

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)
        # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[{
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": name,
                        },
                        "unit_amount": int(amount * 100),
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:5173/cancel",
            )

            # Cache session ID and metadata in Redis
            print('Payment intent:', checkout_session.payment_intent)
            redis_key = f"checkout_session_{checkout_session.id}"
            redis_data = {
                'session_id': checkout_session.id or "",
                'booked_id': int(booked_id) or "",
                'amount': int(amount * 100),
                'name': name or "",
                'category': category or "",
                }

            redis_conn.hset(redis_key, mapping=redis_data)
            redis_conn.expire(redis_key, 3600)  

            # Return session ID
            return JsonResponse({"id": checkout_session.id})

        except Exception as e:
            print("Error:", e)
            return JsonResponse({"error": str(e)}, status=400)




class ConfirmPaymentView(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request, *args, **kwargs):
        session_id = request.data.get("session_id")
        user = request.user if request.user.is_authenticated else None

        if not session_id:
            return JsonResponse({"error": "Session ID not provided"}, status=400)

        if not user:
            return JsonResponse({"error": "User not authenticated"}, status=401)

        try:
            # Retrieve session from Stripe
            session = stripe.checkout.Session.retrieve(session_id)

            # Check payment status
            if session.payment_status == "paid":
                redis_key = f"checkout_session_{session_id}"

                data = redis_conn.hgetall(redis_key)
                if not data:
                    return JsonResponse({"error": "Session data not found in Redis"}, status=400)

                try:
                    booked_id = int(data.get(b"booked_id", 0))
                    amount = int(data.get(b"amount", 0)) / 100
                    name = data.get(b"name", b"").decode("utf-8")
                    category = data.get(b"category", b"").decode("utf-8")
                except ValueError as e:
                    return JsonResponse({"error": f"Invalid data in Redis: {str(e)}"}, status=400)

                if not booked_id or not amount or not category:
                    return JsonResponse({"error": "Incomplete session data"}, status=400)

                booked_id = int(booked_id)

                if category == "package":
                    booked_table = BookedPackage.objects.get(id=booked_id)
                elif category == "flight":
                    booked_table = BookedFlight.objects.get(id=booked_id)
                elif category == "visa":
                    booked_table = VisaBooked.objects.get(id=booked_id)
                else:
                    booked_table = BookedResort.objects.get(id=booked_id)

                # Update payment status
                booked_table.paid_amount = amount
                booked_table.approved_at = timezone.now()
                booked_table.conformed = 'Confirmed'
                booked_table.save()

                # Create payment record with payment_intent
                Payment.objects.create(
                    user=user,
                    method="stripe",
                    amount=amount,
                    transaction_id=session.payment_intent,  # Store payment_intent ID
                    booking_id=booked_table.id,
                    category=category,
                    status="success",
                    date=timezone.now()
                )

                return JsonResponse({"booking_id": booked_table.id, 'amount': amount, 'name': name}, status=200)
            return JsonResponse({"error": "Payment not successful"}, status=400)

        except stripe.error.StripeError as e:
            print(f"Stripe error: {e.error.message}")
            return JsonResponse({"error": e.error.message}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)
        


class RefundPackageView(APIView):
    def get(self, request):
        try:
            booking_id = request.query_params.get('booked_id')
            category = request.query_params.get('category')

            if category == "package":
                booked_table = BookedPackage.objects.get(id=booking_id)
            elif category == "flight":
                booked_table = BookedFlight.objects.get(id=booking_id)
            elif category == "visa":
                booked_table = VisaBooked.objects.get(id=booking_id)
            else:
                booked_table = BookedResort.objects.get(id=booking_id)
            booking = booked_table.objects.get(id=booking_id)
            package = booking.package
            current_date = date.today()

            # Check refund eligibility
            if current_date <= booking.approved_at - timedelta(days=package.full_refund):
                refund_status = "Full refund"
                refund_amount = booking.total_amount
            elif current_date <= booking.approved_at - timedelta(days=package.half_refund):
                refund_status = "Half refund"
                refund_amount = booking.total_amount / 2
            else:
                refund_status = "No refund"
                refund_amount = 0
            print('refund_amount', refund_amount, 'booking', booking)

            return Response({
                "refund_status": refund_status,
                "refund_amount": refund_amount,
            }, status=status.HTTP_200_OK)

        except BookedPackage.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def post(self, request):
        try:
            booking_id = request.data.get('booked_id')
            category = request.data.get('category')
            print('Booking ID:', booking_id, 'Category:', category)

            if category == "package":
                booking = BookedPackage.objects.get(id=booking_id)
                package = booking.package
            elif category == "flight":
                booking = BookedFlight.objects.get(id=booking_id)
            elif category == "visa":
                booking = VisaBooked.objects.get(id=booking_id)
            else:
                booking = BookedResort.objects.get(id=booking_id)
                package = booking.resort
            
            payment = Payment.objects.get(booking_id=booking.id)
            
            current_date = date.today()

            # Check refund eligibility
            created_at_date = booking.created_at.date()

            if current_date >= (created_at_date - timedelta(days=package.full_refund)):
                refund_status = "Full refund"
                refund_amount = booking.total_amount
            elif current_date >= (created_at_date - timedelta(days=package.half_refund)):
                refund_status = "Half refund"
                refund_amount = booking.total_amount // 2
            else:
                refund_status = "No refund"
                refund_amount = 0

            if refund_amount > 0:
                print('Refund Amount:', refund_amount)
                print('Transaction ID:', payment.transaction_id)

                # Process refund through Stripe
                refund = stripe.Refund.create(
                    payment_intent=payment.transaction_id,  # Use payment_intent ID
                    amount=int(refund_amount * 100)  # Convert to cents
                )
                print('Stripe Refund:', refund)

                booking.conformed = "Cancelled"
                booking.save()
                return Response({
                    "refund_status": refund_status,
                    "refund_amount": refund_amount,
                    "stripe_refund_id": refund.id
                }, status=status.HTTP_200_OK)
            else:
                return Response({
                    "refund_status": "No refund",
                    "message": "Refund not applicable"
                }, status=status.HTTP_400_BAD_REQUEST)

        except BookedPackage.DoesNotExist:
            return Response({"error": "Booking not found."}, status=status.HTTP_404_NOT_FOUND)
        except Payment.DoesNotExist:
            return Response({"error": "Payment record not found."}, status=status.HTTP_404_NOT_FOUND)
        except stripe.error.StripeError as e:
            print('Stripe Error:', str(e))
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)