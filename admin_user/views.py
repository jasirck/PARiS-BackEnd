# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Admin 
from users.models import User
from .serializers import AdminLoginSerializer,UserSerializer
from rest_framework.permissions import IsAuthenticated
from admin_user.jwtAuthentication import CustomJWTAuthentication


class AdminLoginView(APIView):

    def post(self, request):
        serializer = AdminLoginSerializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            password = serializer.validated_data['password']
            try:
                user = Admin.objects.get(email=email)
                if user.check_password(password) and user.is_staff and user.is_active:
                    refresh = RefreshToken.for_user(user)
                    access_token = refresh.access_token
                    
                    # Add custom claims to the access token
                    access_token["is_admin"] = True  # Custom claim
                    access_token["user_id"] = user.id  # Include user ID

                    return Response({
                        'refresh': str(refresh),
                        'access': str(access_token),
                        'user': user.username,  
                        'is_admin': True,
                    }, status=status.HTTP_200_OK)
                else:
                    return Response({'detail': 'Invalid credentials or inactive user.'}, status=status.HTTP_400_BAD_REQUEST)
            except Admin.DoesNotExist:
                return Response({'detail': 'User not found.'}, status=status.HTTP_400_BAD_REQUEST)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



class UserListView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        users = User.objects.all()  # Fetch all users
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)

