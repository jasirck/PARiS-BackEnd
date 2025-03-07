from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status


class UserProfileView(APIView):
    permission_classes = [IsAuthenticated]
    authentication_classes = [JWTAuthentication]

    def get(self, request):
        user = request.user
        data = {
            "username": user.username,
            "first_name": user.first_name,
            "last_name": user.last_name,
            "phone_number": getattr(user, "phone_number", ""),
            "email": user.email,
            "user_image": getattr(user, "user_image", None),
        }
        return Response(data, status=status.HTTP_200_OK)

    def put(self, request):
        user = request.user
        user.username = request.data.get("username")
        user.first_name = request.data.get("first_name")
        user.last_name = request.data.get("last_name")
        user.phone_number = request.data.get("phone_number")
        user.email = request.data.get("email")
        user.user_image = request.data.get("profile_image")
        user.save()
        return Response(
            {"message": "Profile updated successfully"}, status=status.HTTP_200_OK
        )
