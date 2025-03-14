from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import VisaBooked
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=VisaBooked)
def send_visa_status_notification(sender, instance, created, **kwargs):
    logger.info("VisaBooked Signal Triggered. Status: %s", instance.conformed)
    if instance.conformed in ["Approved", "Declined"]:
        channel_layer = get_channel_layer()
        message = (
            f"Visa booking for {instance.user.username} has been {instance.conformed}."
        )

        logger.info("Sending message to group: %s", message)
        async_to_sync(channel_layer.group_send)(
            "visa_notifications",
            {
                "type": "send_notification",
                "message": message,
            },
        )
