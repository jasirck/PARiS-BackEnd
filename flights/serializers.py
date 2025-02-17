from rest_framework import serializers
from .models import Flight, BookedFlight
from decimal import Decimal

class FlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flight
        fields = '__all__' 
class BookedFlightSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookedFlight
        fields = '__all__'

    def create(self, validated_data):
        return BookedFlight.objects.create(**validated_data)
    

class BookedFlightGetSerializer(serializers.ModelSerializer):
    flight = FlightSerializer()  # Nested FlightSerializer for full flight details
    flight_price = serializers.DecimalField(source='flight.price', max_digits=10, decimal_places=2)

    class Meta:
        model = BookedFlight
        fields = [
            'id', 
            'flight', 
            'first_name', 
            'last_name', 
            'email', 
            'phone', 
            'flight_price', 
            'conformed', 
            'date_of_birth', 
            'nationality', 
            'passport_number', 
            'passport_expiry_date', 
            'passport_issued_country', 
            'special_requests', 
            'emergency_contact_name', 
            'emergency_contact_phone', 
            'accept_terms', 
            'meal_preference', 
            'created_at'
        ]
