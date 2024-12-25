from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import Payment,User
from rest_framework.permissions import IsAuthenticated,IsAdminUser
from admin_user.jwtAuthentication import CustomJWTAuthentication , CustomAdminJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from json import loads
from packages.models import BookedPackage
from resorts.models import BookedResort
import stripe
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django_redis import get_redis_connection

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
                        "unit_amount": amount * 100,
                    },
                    "quantity": 1,
                }],
                mode="payment",
                success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:5173/cancel",
            )

            # Cache session ID and metadata in Redis
            redis_key = f"checkout_session_{checkout_session.id}"
            redis_data = {
                'session_id': checkout_session.id or "",
                'booked_id': booked_id or "",
                'amount': amount or 0.0,
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
                booked_id = int(data.get(b"booked_id"))
                amount = int(data.get(b"amount"))
                name = data.get(b"name",b'').decode('utf-8') 
                category = data.get(b"category",b'').decode('utf-8')
                booked_id = int(booked_id)

                if category == "package":
                    booked_table = BookedPackage.objects.get(id=booked_id)
                else:
                    booked_table = BookedResort.objects.get(id=booked_id)

                # Update payment status
                booked_table.paid_amount = amount
                booked_table.conformed = 'Confirmed'
                booked_table.save()

                # Create payment record
                Payment.objects.create(
                    user=user,
                    method="stripe",
                    amount=amount,
                    status="success",
                    date=timezone.now()
                )

                return JsonResponse({"booking_id": booked_table.id,'amount': amount,'name':name }, status=200)
            return JsonResponse({"error": "Payment not successful"}, status=400)

        except stripe.error.StripeError as e:
            print(f"Stripe error: {e.error.message}")
            return JsonResponse({"error": e.error.message}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)
















