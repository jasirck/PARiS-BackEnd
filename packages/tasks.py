# Packages/tasks.py

from celery import shared_task
from datetime import datetime, timedelta
from django.utils.timezone import now
from packages.models import BookedPackage, Package
from datetime import date

@shared_task
def update_booked_package_status():
    """
    Check all 'approved' bookings and change their status to 'declined'
    if more than 2 days have passed since 'approved_at' and the status
    hasn't changed.
    """
    two_days_ago = now() - timedelta(days=2)
    bookings = BookedPackage.objects.filter(
        conformed='approved', 
        approved_at__lte=two_days_ago
    )
    bookings.update(conformed='declined')


@shared_task
def update_package_validity():
    """
    Update the validity of packages by checking the end date.
    """
    expired_packages = Package.objects.filter(end__lt=date.today(), valid=True)
    expired_packages.update(valid=False)

