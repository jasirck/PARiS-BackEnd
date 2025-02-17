from channels.generic.websocket import AsyncWebsocketConsumer
import json
import logging
logger = logging.getLogger(__name__)

class NotificationConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        logger.info("WebSocket connected: %s", self.channel_name)
        self.group_name = 'visa_notifications'
        await self.channel_layer.group_add(self.group_name, self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        logger.info("WebSocket disconnected: %s", self.channel_name)
        await self.channel_layer.group_discard(self.group_name, self.channel_name)

    async def send_notification(self, event):
        message = event['message']
        logger.info("Sending notification: %s", message)
        await self.send(text_data=json.dumps({'message': message}))
