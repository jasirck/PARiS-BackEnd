from django.db import models
from resorts.models import Resort
from users.models import User  

class Package(models.Model):
    name = models.CharField(max_length=255)
    price = models.BigIntegerField()
    start = models.DateField()
    end = models.DateField()
    days = models.IntegerField() 
    is_holiday = models.BooleanField()
    resort = models.ForeignKey(Resort, null=True, blank=True, on_delete=models.SET_NULL)
    package_included = models.TextField(null=True, blank=True)
    package_excluded = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    valid = models.BooleanField()
    base_price = models.BigIntegerField()
    adult_price = models.BigIntegerField(null=True, blank=True)
    child_price = models.BigIntegerField(null=True, blank=True)
    category = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Days(models.Model):
    place_photo = models.TextField(null=True, blank=True)
    day = models.IntegerField()
    place_name = models.TextField()
    activity = models.TextField(null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="days_package")  # Added related_name
    resort = models.ForeignKey(Resort, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Day {self.days_day} at {self.place_name}"


class BookedPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    resort = models.ForeignKey(Resort, null=True, blank=True, on_delete=models.SET_NULL)
    adult_count = models.IntegerField()
    child_count = models.IntegerField()
    paid_amount = models.BigIntegerField()
    total_amount = models.BigIntegerField()

    def __str__(self):
        return f"Booking by {self.user.username} for package {self.package.name}"
