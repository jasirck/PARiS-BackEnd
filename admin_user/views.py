# views.py
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate
from .models import Admin 
from users.models import User
from packages.models import Package,BookedPackage
from resorts.models import Resort,BookedResort
from visas.models import Visa
from flights.models import BookedFlight
from .serializers import AdminLoginSerializer,UserSerializer
from rest_framework.permissions import IsAuthenticated
from admin_user.jwtAuthentication import CustomJWTAuthentication
from django.db.models import Sum, Count



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
        users = User.objects.all().order_by('username')
        serializer = UserSerializer(users, many=True)
        return Response(serializer.data)


class DashboardView(APIView):
    # authentication_classes = [CustomJWTAuthentication]
    # permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            # General statistics
            users = User.objects.count()
            packages = Package.objects.count()
            resorts = Resort.objects.count()
            visas = Visa.objects.count()
            flights = BookedFlight.objects.count()

            # Bookings-related statistics
            total_booked_packages = BookedPackage.objects.count()
            total_package_revenue = (
                BookedPackage.objects.aggregate(total_revenue=Sum('paid_amount'))['total_revenue']
                or 0
            )
            total_booked_resorts = BookedResort.objects.count()
            total_resort_revenue = (
                BookedResort.objects.aggregate(total_revenue=Sum('paid_amount'))['total_revenue']
                or 0
            )

            # Popular package and resort
            most_popular_package = (
                BookedPackage.objects.values('package__name')
                .annotate(num_bookings=Count('id'))
                .order_by('-num_bookings')
                .first()
            )
            most_popular_resort = (
                BookedResort.objects.values('resort__name')
                .annotate(num_bookings=Count('id'))
                .order_by('-num_bookings')
                .first()
            )

            data = {
                # General stats
                'users': users,
                'packages': packages,
                'resorts': resorts,
                'visas': visas,
                'flights': flights,

                # Booking stats
                'total_booked_packages': total_booked_packages,
                'total_package_revenue': total_package_revenue,
                'total_booked_resorts': total_booked_resorts,
                'total_resort_revenue': total_resort_revenue,
                'total_revenue': total_package_revenue + total_resort_revenue,

                # Popular items
                'most_popular_package': {
                    'name': most_popular_package['package__name']
                    if most_popular_package
                    else None,
                    'bookings': most_popular_package['num_bookings']
                    if most_popular_package
                    else 0,
                },
                'most_popular_resort': {
                    'name': most_popular_resort['resort__name']
                    if most_popular_resort
                    else None,
                    'bookings': most_popular_resort['num_bookings']
                    if most_popular_resort
                    else 0,
                },
            }

            return Response(data, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
