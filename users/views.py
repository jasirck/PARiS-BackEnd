# accounts/views.py
from django.contrib.auth import authenticate
from .serializers import (
    LoginSerializer,
    UserRegisterSerializer,
    PasswordResetSerializer,
)
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from datetime import datetime, timedelta
from .utils import send_otp
from django.contrib.auth import get_user_model
import random
from django_redis import get_redis_connection
from dateutil.parser import isoparse
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import ValidationError


class LoginView(APIView):

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if serializer.is_valid():
            username = serializer.validated_data["username"]
            password = serializer.validated_data["password"]

            user = authenticate(username=username, password=password)
            if user is not None:
                refresh = RefreshToken.for_user(user)
                access_token = refresh.access_token
                user.last_login = datetime.now()
                user.save()

                refresh["is_admin"] = False
                refresh["user_id"] = user.id
                access_token["is_admin"] = False
                access_token["user_id"] = user.id

                return Response(
                    {
                        "refresh": str(refresh),
                        "token": str(access_token),
                        "user": user.username,
                        "is_admin": user.is_staff,
                        "profile": user.user_image,
                    }
                )
            else:
                return Response(
                    {"detail": "Invalid credentials"},
                    status=status.HTTP_401_UNAUTHORIZED,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


User = get_user_model()


class GoogleLogin(APIView):

    def post(self, request):
        try:
            user_data = request.data.get("user")
            if not user_data:
                return Response({"error": "User data is required."}, status=400)

            email = user_data.get("email")
            first_name = user_data.get("given_name", "")
            last_name = user_data.get("family_name", "")
            picture = user_data.get("picture")

            if not email:
                return Response(
                    {"error": "Email is required for authentication."}, status=400
                )

            user, created = User.objects.get_or_create(
                email=email,
                defaults={
                    "username": email,
                    "first_name": first_name,
                    "last_name": last_name,
                    "is_superuser": False,
                    "user_image": picture,
                },
            )
            if created:
                user.last_login = datetime.now()
                user.save()

            # Generate JWT tokens for the user
            refresh = RefreshToken.for_user(user)
            access_token = refresh.access_token

            refresh["is_admin"] = False
            refresh["user_id"] = user.id
            # Add custom claims to the access token
            access_token["is_admin"] = False
            access_token["user_id"] = user.id

            return Response(
                {
                    "message": "User authenticated successfully",
                    "token": str(access_token),
                    "refresh_token": str(refresh),
                    "user": user.username,
                    "profile": picture,
                    "is_admin": False,
                }
            )

        except Exception as e:
            print(e)
            return Response(
                {"error": "An error occurred during authentication."}, status=500
            )


class RegisterView(APIView):
    def post(self, request, *args, **kwargs):
        print("register view")
        print(request.data)
        serializer = UserRegisterSerializer(data=request.data)

        if serializer.is_valid():
            print("serializer is valid")
            user = serializer.save()  # Save user
            return Response(
                {"message": "User registered successfully.", "user_id": user.id},
                status=status.HTTP_201_CREATED,
            )
        else:
            # Print errors for debugging
            print(serializer.errors)
            # Handle validation errors more specifically
            return Response(
                {"detail": "Registration failed.", "errors": serializer.errors},
                status=status.HTTP_400_BAD_REQUEST,
            )


redis_conn = get_redis_connection("default")


class SendOtpView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")
        
        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(phone_number) != 10:
            return Response(
                {"error": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST
            )
        # Check if the phone number already exists in the database
        if User.objects.filter(phone_number=phone_number).exists():
            return Response(
                {"error": "This number is already registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp = send_otp(phone_number)
        otp = random.randint(100000, 999999)
        otp_send_time = datetime.now()
        print(otp)

        redis_key = f"otp:{phone_number}"
        otp_data = {
            "otp": otp,
            "phone_number": phone_number,
            "otp_send_time": otp_send_time.isoformat(),
        }

        # Use hset instead of deprecated hmset
        redis_conn.hset(redis_key, mapping=otp_data)
        redis_conn.expire(redis_key, 300)  # Set expiration to 5 minutes

        return Response({"message": "OTP sent successfully"}, status=status.HTTP_200_OK)


class SendOtpForgotView(APIView):
    def post(self, request):
        phone_number = request.data.get("phone_number")

        if not phone_number:
            return Response(
                {"error": "Phone number is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if len(phone_number) != 10:
            return Response(
                {"error": "Invalid phone number"}, status=status.HTTP_400_BAD_REQUEST
            )
        
        if User.objects.filter(phone_number=phone_number).exists():
            otp = send_otp(phone_number)
            otp = random.randint(100000, 999999)
            otp_send_time = datetime.now()
            print(otp)

            redis_key = f"otp:{phone_number}"
            otp_data = {
                "otp": otp,
                "phone_number": phone_number,
                "otp_send_time": otp_send_time.isoformat(),
            }

            # Use hset instead of deprecated hmset
            redis_conn.hset(redis_key, mapping=otp_data)
            redis_conn.expire(redis_key, 300)  

            return Response(
                {"message": "OTP sent successfully"}, status=status.HTTP_200_OK
            )

        else:
            return Response(
                {"error": "This number is Not registered"},
                status=status.HTTP_400_BAD_REQUEST,
            )


class VerifyOtpView(APIView):
    def post(self, request):
        user_otp = request.data.get("otp")
        phone_number = request.data.get("phone_number")

        if not user_otp or not phone_number:
            return Response(
                {"error": "OTP and phone number are required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        redis_key = f"otp:{phone_number}"
        otp_data = redis_conn.hgetall(redis_key)

        if not otp_data:
            return Response(
                {"error": "OTP has expired or does not exist"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        stored_otp = otp_data.get(b"otp")
        otp_send_time = otp_data.get(b"otp_send_time")

        if not stored_otp or not otp_send_time:
            return Response(
                {"error": "OTP data is incomplete or missing"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        otp_send_time = isoparse(otp_send_time.decode("utf-8"))
        current_time = datetime.now()

        if current_time - otp_send_time > timedelta(minutes=2):
            redis_conn.delete(redis_key)  # Delete expired OTP
            return Response(
                {"error": "OTP has expired"}, status=status.HTTP_400_BAD_REQUEST
            )

        if str(user_otp) == stored_otp.decode("utf-8"):
            redis_conn.delete(redis_key)
            return Response(
                {"message": "OTP verified successfully"}, status=status.HTTP_200_OK
            )

        return Response({"error": "Incorrect OTP"}, status=status.HTTP_400_BAD_REQUEST)


class RefreshTokenView(APIView):

    def post(self, request):
        refresh_token = request.data.get("refresh_token")
        if not refresh_token:
            return Response(
                {"detail": "Refresh token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )
        try:
            refresh = RefreshToken(refresh_token)
            token = refresh.access_token
            token["is_admin"] = (
                refresh["is_admin"] if refresh["is_admin"] in refresh else False
            )
            token["user_id"] = (
                refresh["user_id"] if refresh["user_id"] in refresh else None
            )
            return Response({"access": str(token)}, status=status.HTTP_200_OK)
        except Exception as e:
            print("RefreshTokenView", e)
            return Response(
                {"detail": "Invalid refresh token"}, status=status.HTTP_401_UNAUTHORIZED
            )


class PasswordResetView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = PasswordResetSerializer(data=request.data)

        if serializer.is_valid():
            try:
                serializer.save()
                return Response(
                    {"message": "Password reset successful."}, status=status.HTTP_200_OK
                )
            except ValidationError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)
            except Exception as e:
                return Response(
                    {"error": "An unexpected error occurred."},
                    status=status.HTTP_500_INTERNAL_SERVER_ERROR,
                )

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
