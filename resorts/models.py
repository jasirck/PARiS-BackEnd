from django.db import models
from users.models import User 

class Resort(models.Model):
    resort_name = models.CharField(max_length=255)
    resort_location = models.CharField(max_length=255)
    pool = models.BooleanField()
    package_inclusions = models.TextField(null=True, blank=True)
    base_price = models.BigIntegerField()
    adult_price = models.BigIntegerField(null=True, blank=True)
    child_price = models.BigIntegerField(null=True, blank=True)
    policy = models.TextField(null=True, blank=True)
    valid = models.BooleanField()


    def __str__(self):
        return self.resort_name

class ResortImages(models.Model):
    resort = models.ForeignKey('Resort', on_delete=models.CASCADE)
    image = models.TextField()


    def __str__(self):
        return f"Resort: {self.resort.resort_name}, Image: {self.image}"


class BookedResort(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, on_delete=models.CASCADE)
    price = models.BigIntegerField()
    days = models.IntegerField()
    adults = models.IntegerField()
    children = models.IntegerField()

    def __str__(self):
        return f"Booking by {self.user.username} at {self.resort.resort_name}"
