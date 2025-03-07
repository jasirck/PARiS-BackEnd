from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Package, Days, BookedPackage, PackageCategory
from users.models import User
from .serializers import (
    PackageSerializer,
    DaysSerializer,
    BookedPackageSerializer,
    UserPackageSerializer,
    CategorySerializer,
)
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from admin_user.jwtAuthentication import (
    CustomJWTAuthentication,
    CustomAdminJWTAuthentication,
)
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.shortcuts import get_object_or_404
from json import loads
import stripe
from payments.models import Payment
from django.conf import settings
from django.http import JsonResponse
from rest_framework.exceptions import NotFound
from django.utils import timezone
from django_redis import get_redis_connection


redis_conn = get_redis_connection("default")


class PackageView(APIView):
    def get(self, request):
        packages = Package.objects.prefetch_related("days_package").filter(
            is_holiday=False, valid=True
        )
        serializer = UserPackageSerializer(packages, many=True)
        return Response(serializer.data)


class HolidaysView(APIView):
    def get(self, request):
        packages = Package.objects.prefetch_related("days_package").filter(
            is_holiday=True, valid=True
        )
        serializer = UserPackageSerializer(packages, many=True)
        return Response(serializer.data)


class AdminPackageView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk=None):
        # Package.update_validity()
        if pk:
            package = Package.objects.get(id=pk)
            days = Days.objects.filter(package=package.id)
            package_serializer = PackageSerializer(package)
            days_serializer = DaysSerializer(days, many=True)
            result = {
                "package": package_serializer.data,
                "days": days_serializer.data,
            }
            return Response(result, status=200)
        else:
            # List all packages
            packages = Package.objects.filter(is_holiday=False).order_by("name")
            serializer = PackageSerializer(packages, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        package_data = request.data

        # Parse the days_package JSON string into a Python list
        day_plans = loads(package_data.get("days_package", "[]"))

        # Handle the Package serialization
        package_serializer = PackageSerializer(data=package_data)

        if package_serializer.is_valid():
            # Save the Package instance first
            package = package_serializer.save()

            # Handle the Days data
            for day_data in day_plans:
                # Assign the saved package's ID to each day plan
                day_data["package"] = package.id

                # Serialize and save each day plan
                day_serializer = DaysSerializer(data=day_data)
                if day_serializer.is_valid():
                    day_serializer.save()
                else:
                    # Print errors inside the loop
                    print(day_serializer.errors)
                    return Response(
                        day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(package_serializer.data, status=status.HTTP_201_CREATED)

        # If package_serializer is not valid, print its errors
        print(package_serializer.errors)
        return Response(package_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Handles PUT requests."""
        package = get_object_or_404(Package, pk=pk)
        print(request.data)
        package_data = request.data
        day_plans = loads(package_data.get("days_package", "[]"))
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            for day_data in day_plans:
                # Assign the saved package's ID to each day plan
                day_data["package"] = package.id

                # Serialize and save each day plan
                day_serializer = DaysSerializer(data=day_data)
                if day_serializer.is_valid():
                    day_serializer.save()
                else:
                    # Print errors inside the loop
                    print(day_serializer.errors)
                    return Response(
                        day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Handles DELETE requests."""
        # Check if package exists
        package = get_object_or_404(Package, pk=pk)

        # Check if there are any related days before deleting
        if Days.objects.filter(package=package).exists():
            return Response(
                {"error": "Cannot delete package as it is referenced in other tables."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed to delete related days
        Days.objects.filter(package=package).delete()

        # Delete the package
        package.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class PackageDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        try:
            package = Package.objects.get(id=pk)
            days = Days.objects.filter(package=package.id)
            package_serializer = PackageSerializer(package)
            days_serializer = DaysSerializer(days, many=True)
            result = {
                "package": package_serializer.data,
                "days": days_serializer.data,
            }
            return Response(result, status=200)
        except Package.DoesNotExist:
            raise NotFound(detail="Package not found.")


class BookedPackageView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        package = get_object_or_404(Package, id=data.get("package"))
        total_amount = (
            (package.adult_price * data.get("adult_count", 0))
            + (package.child_price * data.get("child_count", 0))
            + package.base_price
        )
        data["total_amount"] = total_amount
        data["paid_amount"] = 0
        data["user"] = user.id

        serializer = BookedPackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        print(request.user)
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedPackage, pk=pk)
            serializer = BookedPackageSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings with the updated filter
            bookings = BookedPackage.objects.filter(
                package__is_holiday=False, package__valid=True
            ).order_by("-date")
            print(bookings)
            serializer = BookedPackageSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBookedpackageView(APIView):
    authentication_classes = [CustomAdminJWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedPackage, pk=pk)
            serializer = BookedPackageSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedPackage.objects.filter(
                package__is_holiday=False, package__valid=True
            ).order_by("-date")
            print(bookings)
            serializer = BookedPackageSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        id = request.data.get("id")
        status_value = request.data.get("status")
        print(id, status)
        try:
            booking = BookedPackage.objects.get(id=id)
            booking.conformed = status_value
            booking.save()
            return Response(
                {"message": "Holiday request approved successfully"},
                status=status.HTTP_200_OK,
            )
        except BookedPackage.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        booking = get_object_or_404(BookedPackage, pk=pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class AdminHolidayView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomAdminJWTAuthentication]

    def get(self, request, pk=None):
        print(request.data)
        if pk:
            holiday = Package.objects.get(id=pk)
            days = Days.objects.filter(package=holiday.id)
            package_serializer = PackageSerializer(holiday)
            days_serializer = DaysSerializer(days, many=True)
            result = {
                "holiday": package_serializer.data,
                "days": days_serializer.data,
            }
            return Response(result, status=200)
        else:
            # List all packages
            holidays = Package.objects.filter(is_holiday=True).order_by("name")
            serializer = PackageSerializer(holidays, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """Handles POST requests."""
        holiday_data = request.data
        print(holiday_data)

        # Parse the days_holiday JSON string into a Python list
        day_plans = loads(holiday_data.get("days_holiday", "[]"))

        # Handle the holiday serialization
        holiday_serializer = PackageSerializer(data=holiday_data)

        if holiday_serializer.is_valid():
            # Save the holiday instance first
            holiday = holiday_serializer.save()

            # Handle the Days data
            for day_data in day_plans:
                # Assign the saved package's ID to each day plan
                day_data["package"] = holiday.id

                # Serialize and save each day plan
                day_serializer = DaysSerializer(data=day_data)
                if day_serializer.is_valid():
                    day_serializer.save()
                else:
                    # Print errors inside the loop
                    print(day_serializer.errors)
                    return Response(
                        day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(holiday_serializer.data, status=status.HTTP_201_CREATED)

        # If package_serializer is not valid, print its errors
        print(
            "holiday_data:",
            holiday_data,
            "holiday_serializer:",
            holiday_serializer.errors,
        )
        return Response(holiday_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def put(self, request, pk):
        """Handles PUT requests."""
        package = get_object_or_404(Package, pk=pk)
        print(request.data)
        holiday_data = request.data
        day_plans = loads(holiday_data.get("days_holiday", "[]"))
        serializer = PackageSerializer(package, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            for day_data in day_plans:
                # Assign the saved package's ID to each day plan
                day_data["package"] = package.id

                # Serialize and save each day plan
                day_serializer = DaysSerializer(data=day_data)
                if day_serializer.is_valid():
                    day_serializer.save()
                else:
                    # Print errors inside the loop
                    print(day_serializer.errors)
                    return Response(
                        day_serializer.errors, status=status.HTTP_400_BAD_REQUEST
                    )

            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """Handles DELETE requests."""
        # Check if package exists
        package = get_object_or_404(Package, pk=pk)

        # Check if there are any related days before deleting
        if Days.objects.filter(package=package).exists():
            return Response(
                {"error": "Cannot delete package as it is referenced in other tables."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Proceed to delete related days
        Days.objects.filter(package=package).delete()

        # Delete the package
        package.delete()

        return Response(status=status.HTTP_204_NO_CONTENT)


class HolidayDetailsView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request, pk):
        try:
            package = Package.objects.get(id=pk)
            days = Days.objects.filter(package=package.id)
            package_serializer = PackageSerializer(package)
            days_serializer = DaysSerializer(days, many=True)
            result = {
                "package": package_serializer.data,
                "days": days_serializer.data,
            }
            return Response(result, status=200)
        except Package.DoesNotExist:
            raise NotFound(detail="Package not found.")


class BookedHolidayView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        data = request.data
        package = get_object_or_404(Package, id=data.get("package"))
        total_amount = (
            (package.adult_price * data.get("adult_count", 0))
            + (package.child_price * data.get("child_count", 0))
            + package.base_price
        )
        data["total_amount"] = total_amount
        data["paid_amount"] = 0
        data["user"] = user.id

        serializer = BookedPackageSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        print(serializer.errors)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def get(self, request, pk=None):
        print(request.user)
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedPackage, pk=pk)
            serializer = BookedPackageSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedPackage.objects.filter(
                user=request.user, package__is_holiday=True
            ).order_by("-date")
            print(bookings)
            serializer = BookedPackageSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)


class AdminBookedHolidayView(APIView):
    authentication_classes = [CustomAdminJWTAuthentication]
    permission_classes = [IsAdminUser]

    def get(self, request, pk=None):
        if pk:
            # Retrieve a specific booking
            booking = get_object_or_404(BookedPackage, pk=pk)
            serializer = BookedPackageSerializer(booking)
            return Response(serializer.data, status=status.HTTP_200_OK)
        else:
            # List all bookings
            bookings = BookedPackage.objects.filter(package__is_holiday=True).order_by(
                "-date"
            )
            print(bookings)
            serializer = BookedPackageSerializer(bookings, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        id = request.data.get("id")
        status_value = request.data.get("status")
        print(id, status)
        try:
            booking = BookedPackage.objects.get(id=id)
            booking.conformed = status_value
            booking.save()
            return Response(
                {"message": "Holiday request approved successfully"},
                status=status.HTTP_200_OK,
            )
        except BookedPackage.DoesNotExist:
            return Response(
                {"error": "Booking not found"}, status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            print(e)
            return Response(
                {"error": "An error occurred"}, status=status.HTTP_400_BAD_REQUEST
            )

    def delete(self, request, pk):
        booking = get_object_or_404(BookedPackage, pk=pk)
        booking.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CategoryView(APIView):
    permission_classes = [IsAdminUser]
    authentication_classes = [CustomJWTAuthentication]

    def get(self, request, pk=None):
        if pk:
            try:
                category = PackageCategory.objects.get(pk=pk)
                print("get", categories)
            except PackageCategory.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        else:
            categories = PackageCategory.objects.all()
            serializer = CategorySerializer(categories, many=True)
            return Response(serializer.data)

    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def patch(self, request, pk=None):
        if pk:
            try:

                category = PackageCategory.objects.get(pk=pk)
                print(category)
            except PackageCategory.DoesNotExist:
                return Response(status=status.HTTP_404_NOT_FOUND)

            serializer = CategorySerializer(
                category, data=request.data, partial=True
            )  # Partial update
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response(status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        try:
            category = PackageCategory.objects.get(id=pk)
            category.delete()
            return Response(
                {"message": "Category deleted successfully"},
                status=status.HTTP_204_NO_CONTENT,
            )
        except PackageCategory.DoesNotExist:
            return Response(
                {"error": "Category not found"}, status=status.HTTP_404_NOT_FOUND
            )


class CategoryShowView(APIView):
    def get(
        self,
        request,
    ):
        categories = PackageCategory.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)


stripe.api_key = settings.STRIPE_TEST_SECRET_KEY


class CreateCheckoutSessionView(APIView):
    def post(self, request, *args, **kwargs):

        try:
            data = request.data
            amount = data.get("amount", 0)
            name = data.get("name")
            booked_id = data.get("booked_id")

            print("Received data:", data)

            # Validate input
            if not amount or amount <= 0:
                return JsonResponse({"error": "Invalid amount"}, status=400)

            if not name:
                return JsonResponse({"error": "Name is required"}, status=400)
            # Create Stripe checkout session
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=["card"],
                line_items=[
                    {
                        "price_data": {
                            "currency": "inr",
                            "product_data": {
                                "name": name,
                            },
                            "unit_amount": amount * 100,
                        },
                        "quantity": 1,
                    }
                ],
                mode="payment",
                success_url="http://localhost:5173/success?session_id={CHECKOUT_SESSION_ID}",
                cancel_url="http://localhost:5173/cancel",
            )

            print("checkout_session:", checkout_session)
            redis_key = f"checkout_session_{checkout_session.id}"
            redis_data = {
                "session_id": checkout_session.id or "",
                "booked_id": booked_id or "",
                "amount": amount or 0.0,
                "name": name or "",
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
                name = data.get(b"name", b"").decode("utf-8")
                booked_id = int(booked_id)
                booked_package = BookedPackage.objects.get(id=booked_id)
                booked_package.paid_amount = amount
                booked_package.conformed = "Confirmed"
                booked_package.save()

                # Create payment record
                Payment.objects.create(
                    user=user,
                    method="stripe",
                    amount=amount,
                    status="success",
                    date=timezone.now(),
                )

                return JsonResponse(
                    {"booking_id": booked_package.id, "amount": amount, "name": name},
                    status=200,
                )
            return JsonResponse({"error": "Payment not successful"}, status=400)

        except stripe.error.StripeError as e:
            print(f"Stripe error: {e.error.message}")
            return JsonResponse({"error": e.error.message}, status=400)
        except Exception as e:
            print(f"Unexpected error: {str(e)}")
            return JsonResponse({"error": "An unexpected error occurred"}, status=500)
