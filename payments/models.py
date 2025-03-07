# Payment.modals
from django.db import models
from users.models import User
from packages.models import BookedPackage

# Create your models here.


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="payments")
    method = models.CharField(max_length=50)
    status = models.CharField(max_length=50)
    transaction_id = models.CharField(max_length=100)
    booking_id = models.IntegerField(default=None, null=True, blank=True)
    category = models.CharField(max_length=50)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    massage = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"Payment for Booking ID {self.booking.id} - {self.status}"
