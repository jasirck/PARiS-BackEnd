from django.db import models
from users.models import User  

class Visa(models.Model):
    name = models.CharField(verbose_name="Visa Name")
    place_photo = models.TextField(verbose_name="Place Photo")
    category = models.ForeignKey("VisaCategory", on_delete=models.CASCADE, related_name="visa_category")
    note = models.TextField(verbose_name="Note")

    def __str__(self):
        return self.name


class VisaDays(models.Model):
    visa = models.ForeignKey(Visa, on_delete=models.CASCADE, related_name="visa_days")
    days = models.IntegerField(verbose_name="Number of Days")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Visa Price")
    

    def __str__(self):
        return f"{self.visa.name} - {self.days} Days"

class VisaCategory(models.Model):
    name = models.CharField(verbose_name="Visa Category Name")
    description = models.TextField(verbose_name="Visa Category Description")

    def __str__(self):
        return self.name

class VisaBooked(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="visa_bookings")
    days = models.ForeignKey(VisaDays, on_delete=models.CASCADE, related_name="visa_days")
    passport = models.TextField(verbose_name="Passport Photo")
    photo = models.TextField(verbose_name="Personal Photo")
    booked_visa = models.ForeignKey(Visa, on_delete=models.CASCADE, related_name="bookings")
    conformed = models.CharField(max_length=50, default='Requested')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.booked_visa.name}"
