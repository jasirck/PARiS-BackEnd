import pytest
import json
import datetime
import pytz
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from rest_framework.test import APITestCase
from django.urls import reverse
from messege.consumers import AdminChatConsumer, UserChatConsumer

User = get_user_model()


@pytest.mark.asyncio
class ChatConsumerTests(APITestCase):
    """Test WebSocket consumers for real-time chat"""

    def setUp(self):
        """Create test users and obtain authentication tokens"""
        self.admin_user = User.objects.create_superuser(
            username="admin", email="admin@example.com", password="adminpass"
        )
        self.user = User.objects.create_user(
            username="user", email="user@example.com", password="userpass"
        )

        # Obtain JWT token for admin
        response = self.client.post(
            reverse("token_obtain_pair"), {"username": "admin", "password": "adminpass"}
        )
        self.admin_token = response.data.get("access")

        # Obtain JWT token for normal user
        response = self.client.post(
            reverse("token_obtain_pair"), {"username": "user", "password": "userpass"}
        )
        self.user_token = response.data.get("access")

        # Ensure datetime values are timezone-aware
        self.timestamp = datetime.datetime.now(pytz.UTC)

    async def test_admin_connect(self):
        """Test if admin can successfully connect to WebSocket"""
        communicator = WebsocketCommunicator(
            AdminChatConsumer.as_asgi(), f"/ws/admin/chat/?token={self.admin_token}"
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_user_connect(self):
        """Test if user can successfully connect to WebSocket"""
        communicator = WebsocketCommunicator(
            UserChatConsumer.as_asgi(), f"/ws/user/chat/?token={self.user_token}"
        )
        connected, _ = await communicator.connect()
        assert connected is True
        await communicator.disconnect()

    async def test_admin_send_message(self):
        """Test if admin can send a chat message"""
        communicator = WebsocketCommunicator(
            AdminChatConsumer.as_asgi(), f"/ws/admin/chat/?token={self.admin_token}"
        )
        await communicator.connect()

        message_data = {
            "message": "Hello User!",
            "receiver_id": self.user.id,
            "is_sender_admin": True,
        }

        await communicator.send_json_to(message_data)
        response = await communicator.receive_json_from()
        assert response["message"] == "Hello User!"
        await communicator.disconnect()

    async def test_chat_history(self):
        """Test fetching chat history"""
        from messege.models import ChatMessage

        # Create sample messages
        ChatMessage.objects.create(
            sender=self.user,
            receiver=self.admin_user,
            content="Test Message 1",
            timestamp=self.timestamp,
        )
        ChatMessage.objects.create(
            sender=self.admin_user,
            receiver=self.user,
            content="Test Message 2",
            timestamp=self.timestamp,
        )

        response = self.client.get(
            reverse("chat-history", args=[self.user.id, self.admin_user.id])
        )
        assert response.status_code == 200
        assert len(response.data) == 2  # Two messages in history

    async def test_unread_messages(self):
        """Test retrieving unread messages"""
        from messege.models import ChatMessage

        ChatMessage.objects.create(
            sender=self.user,
            receiver=self.admin_user,
            content="Unread Message",
            timestamp=self.timestamp,
            is_read=False,
        )

        response = self.client.get(
            reverse("unread-messages", args=[self.admin_user.id])
        )
        assert response.status_code == 200
        assert len(response.data) == 1  # One unread message
