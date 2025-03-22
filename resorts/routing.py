from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path("ws/resort_notifications/", consumers.NotificationConsumer.as_asgi()),
]
