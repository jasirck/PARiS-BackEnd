from django.db import models
from users.models import User
class Flight(models.Model):
    flight_number = models.CharField(max_length=50)
    departure_city = models.CharField(max_length=100)
    arrival_city = models.CharField(max_length=100) 
    departure_date = models.DateTimeField()
    arrival_date = models.DateTimeField() 
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.flight_number} ({self.departure_city} to {self.arrival_city})"

class BookedFlight(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    flight = models.ForeignKey(Flight, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    date_of_birth = models.DateField()
    nationality = models.CharField(max_length=100)
    passport_number = models.CharField(max_length=50)
    passport_expiry_date = models.DateField()
    passport_issued_country = models.CharField(max_length=100)
    special_requests = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100)
    emergency_contact_phone = models.CharField(max_length=20)
    accept_terms = models.BooleanField(default=False)
    meal_preference = models.CharField(max_length=50, blank=True)
    conformed = models.CharField(max_length=50, default='Pending')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking for {self.first_name} {self.last_name} on flight {self.flight}"
