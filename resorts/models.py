from django.db import models
from users.models import User 

class Resort(models.Model):
    name = models.CharField(max_length=255,unique=True)
    location = models.CharField(max_length=255)
    pool = models.BooleanField()
    package_inclusions = models.TextField(null=True, blank=True)
    base_price = models.BigIntegerField()
    adult_price = models.BigIntegerField(null=True, blank=True)
    child_price = models.BigIntegerField(null=True, blank=True)
    policy = models.TextField(null=True, blank=True)
    valid = models.BooleanField( default=True)
    category = models.ForeignKey("ResortCategory", on_delete=models.CASCADE,related_name="Resort_category")



    def __str__(self):
        return self.name

class ResortImages(models.Model):
    resort = models.ForeignKey('Resort',related_name='images', on_delete=models.CASCADE)
    image = models.URLField()


    def __str__(self):
        return f"Resort: {self.resort.name}, Image: {self.image}"


class BookedResort(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE)
    paid_amount = models.BigIntegerField(default=0)
    total_amount = models.BigIntegerField()
    days = models.IntegerField()
    adults = models.IntegerField()
    children = models.IntegerField()
    start_date = models.DateField()
    end_date = models.DateField()
    conformed = models.CharField( max_length=50,default='Requested')
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"Booking by {self.user.username} at {self.resort.name}"


class ResortCategory(models.Model):
    name = models.CharField(max_length=255,unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name
