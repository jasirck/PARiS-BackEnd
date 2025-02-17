# Packages.models

from django.db import models
from resorts.models import Resort
from users.models import User  
from django.utils import timezone
from datetime import timedelta
from django.db.models.signals import post_save
from django.dispatch import receiver
from datetime import date

class Package(models.Model):
    name = models.CharField(max_length=255, unique=True)
    start = models.DateField()
    end = models.DateField()
    days = models.IntegerField()
    is_holiday = models.BooleanField()
    package_included = models.TextField(null=True, blank=True)
    package_excluded = models.TextField(null=True, blank=True)
    note = models.TextField(null=True, blank=True)
    valid = models.BooleanField(default=True)
    base_price = models.BigIntegerField()
    adult_price = models.BigIntegerField(null=True, blank=True)
    child_price = models.BigIntegerField(null=True, blank=True)
    category = models.ForeignKey("PackageCategory", on_delete=models.CASCADE, related_name="package_category")
    full_refund = models.IntegerField(default=14)  
    half_refund = models.IntegerField(default=7)  

    def __str__(self):
        return self.name


class Days(models.Model):
    place_photo = models.TextField(null=True, blank=True)
    day = models.IntegerField()
    place_name = models.TextField()
    activity = models.TextField(null=True, blank=True)
    package = models.ForeignKey(Package, on_delete=models.CASCADE, related_name="days_package")
    resort = models.ForeignKey(Resort, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Day {self.day} at {self.place_name}"


def default_date_plus_20_days():
    return timezone.now().date() + timedelta(days=20)


class BookedPackage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    package = models.ForeignKey(Package, on_delete=models.CASCADE)
    adult_count = models.IntegerField()
    child_count = models.IntegerField()
    paid_amount = models.BigIntegerField()
    total_amount = models.BigIntegerField()
    date = models.DateField(default=default_date_plus_20_days)
    conformed = models.CharField(max_length=50, default='Requested')
    approved_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    

    def __str__(self):
        
        return f"Booking by {self.user.username} for package {self.package.name}"


class PackageCategory(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(null=True, blank=True)

    def __str__(self):
        return self.name


@receiver(post_save, sender=BookedPackage)
def set_approved_at(sender, instance, created, **kwargs):
    if instance.conformed == 'approved' and not instance.approved_at:
        instance.approved_at = timezone.now()
        instance.save()

