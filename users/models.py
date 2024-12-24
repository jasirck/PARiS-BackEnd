from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    phone_number = models.BigIntegerField(unique=True, null=True, blank=True)
    email = models.EmailField(unique=True)
    user_image = models.TextField(null=True, blank=True)  
    first_join = models.DateField(auto_now_add=True) 
    last_join = models.DateField(auto_now=True) 
    
    def __str__(self):
        return self.username


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    method = models.CharField(max_length=255)
    amount = models.BigIntegerField()  # Amount in cents
    status = models.CharField(max_length=255)
    date = models.DateTimeField()

    def __str__(self):
        return f"Payment {self.id} by {self.user.username} via {self.method}"