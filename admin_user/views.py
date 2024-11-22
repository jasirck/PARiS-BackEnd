# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Admin  # Import your custom Admin model
from .serializers import AdminLoginSerializer


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




