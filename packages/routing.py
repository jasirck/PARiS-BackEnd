from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/visa_notifications/", consumers.NotificationConsumer.as_asgi()),
]
