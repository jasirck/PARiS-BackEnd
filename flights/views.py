from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .utils import get_flights  
from admin_user.jwtAuthentication import CustomJWTAuthentication , CustomAdminJWTAuthentication
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticated,IsAdminUser
import json
from .serializers import BookedFlightSerializer, FlightSerializer,BookedFlightGetSerializer
from .models import BookedFlight

class FlightSearchView(APIView):
    def post(self, request):
        from_city = request.data.get('from')
        to_city = request.data.get('to')
        travel_date = request.data.get('date')

        try:
            flights = get_flights(from_city, to_city, travel_date)
            
            # print(json.dumps(flights[0], indent=4))

            return Response({'flights': flights}, status=status.HTTP_200_OK)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        


class BookFlightView(APIView):
    authentication_classes = [CustomJWTAuthentication]
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            # Extract flight data and create Flight instance
            flight_data = request.data.get('flightData', {})
            print("Incoming flight data:", flight_data)  # Debug print
            
            flight_serializer = FlightSerializer(data=flight_data)
            if not flight_serializer.is_valid():
                print("Flight serializer errors:", flight_serializer.errors)  # Debug print
                return Response(flight_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            flight = flight_serializer.save()
            print("Created flight with ID:", flight.id)  # Debug print

            # Prepare booking data
            booking_data = request.data.get('data', {})
            
            # Convert camelCase to snake_case for booking data
            transformed_booking_data = {
                'first_name': booking_data.get('firstName'),
                'last_name': booking_data.get('lastName'),
                'email': booking_data.get('email'),
                'phone': booking_data.get('phone'),
                'date_of_birth': booking_data.get('dateOfBirth'),
                'nationality': booking_data.get('nationality'),
                'passport_number': booking_data.get('passportNumber'),
                'passport_expiry_date': booking_data.get('passportExpiryDate'),
                'passport_issued_country': booking_data.get('passportIssuedCountry'),
                'special_requests': booking_data.get('specialRequests', ''),
                'emergency_contact_name': booking_data.get('emergencyContactName'),
                'emergency_contact_phone': booking_data.get('emergencyContactPhone'),
                'accept_terms': booking_data.get('acceptTerms'),
                'meal_preference': booking_data.get('mealPreference', ''),
                'conformed': 'pending',
                'flight': flight.id,
                'user': request.user.id
            }

            print("Transformed booking data:", transformed_booking_data)  # Debug print
            
            booked_flight_serializer = BookedFlightSerializer(data=transformed_booking_data)
            if not booked_flight_serializer.is_valid():
                print("BookedFlight serializer errors:", booked_flight_serializer.errors)  # Debug print
                flight.delete()
                return Response(booked_flight_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            booked_flight = booked_flight_serializer.save()
            print("Successfully created booking with ID:", booked_flight.id)  # Debug print
            
            return Response({
                'message': 'Flight booked successfully',
                'id': booked_flight.id,
                'payment_status': booked_flight.conformed
            }, status=status.HTTP_201_CREATED)

        except Exception as e:
            print("Exception occurred:", str(e))  # Debug print
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    def get(self, request, *args, **kwargs):
        # Get all booked flights for the authenticated user
        booked_flights = BookedFlight.objects.filter(user=request.user)
        serializer = BookedFlightGetSerializer(booked_flights, many=True)
        return Response(serializer.data)