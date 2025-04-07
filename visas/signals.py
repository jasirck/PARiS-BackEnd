from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VisaBooked
from packages.models import BookedPackage
from resorts.models import BookedResort
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=BookedPackage)
def send_package_status_notification(sender, instance, created, **kwargs):
    if instance.conformed in ["Approved", "Declined"]:
        channel_layer = get_channel_layer()
        message = f"Package booking for {instance.user.username} has been {instance.conformed}."
        logger.info("Sending package notification: %s", message)
        async_to_sync(channel_layer.group_send)(
            "all_notifications",  # Send to the single group
            {
                "type": "send_notification",
                "message": message,
            },
        )


@receiver(post_save, sender=BookedResort)
def send_resort_status_notification(sender, instance, created, **kwargs):
    if instance.conformed in ["Approved", "Declined"]:
        channel_layer = get_channel_layer()
        message = f"Resort booking for {instance.user.username} has been {instance.conformed}."
        logger.info("Sending resort notification: %s", message)
        async_to_sync(channel_layer.group_send)(
            "all_notifications",  # Send to the single group
            {
                "type": "send_notification",
                "message": message,
            },
        )


@receiver(post_save, sender=VisaBooked)
def send_visa_status_notification(sender, instance, created, **kwargs):
    if instance.conformed in ["Approved", "Declined"]:
        channel_layer = get_channel_layer()
        message = f"Visa booking for {instance.user.username} has been {instance.conformed}."
        logger.info("Sending visa notification: %s", message)
        async_to_sync(channel_layer.group_send)(
            "all_notifications",  # Send to the single group
            {
                "type": "send_notification",
                "message": message,
            },
        )