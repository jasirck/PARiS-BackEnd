import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from rest_framework_simplejwt.tokens import AccessToken
from datetime import datetime
from django.db import models
from users.models import User
from admin_user.models import Admin
from messege.models import ChatMessage, ChatSession
from django.utils import timezone
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
import jwt

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        # Parse the token from query string
        query_string = self.scope["query_string"].decode("utf-8")
        token = query_string.split("=")[1] if "token=" in query_string else None

        if not token:
            await self.close(code=4001)  # Close connection if no token is provided
            return

        # Validate token and fetch user or admin
        try:
            access_token = AccessToken(token)
            user_id = access_token["user_id"]
            is_admin = access_token.get("is_admin", False)

            if is_admin:
                self.admin = await database_sync_to_async(Admin.objects.get)(id=user_id, is_active=True)
                self.user = None
            else:
                self.user = await database_sync_to_async(User.objects.get)(id=user_id, is_active=True)
                self.admin = None

        except (User.DoesNotExist, Admin.DoesNotExist, InvalidToken, TokenError) as e:
            await self.close(code=4001)  
            return

        # Set up appropriate room group name based on user type
        if self.user:
            self.room_group_name = f"chat_user_{self.user.id}"
            self.user_type = "user"
        else:
            self.room_group_name = "admin"
            self.user_type = "admin"

        # Join the WebSocket room
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)
        await self.accept()

        # Send chat history to the user or admin
        if self.user:
            chat_history = await self.get_chat_history(self.user.id)
            await self.send(text_data=json.dumps({
                "type": "chat_history",
                "messages": chat_history,
            }))
        elif self.admin:
            active_sessions = await self.get_active_chat_sessions()
            await self.send(text_data=json.dumps({
                "type": "contact_list",
                "contacts": active_sessions
            }))

    async def disconnect(self, close_code):
        if hasattr(self, "room_group_name"):
            await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        try:
            data = json.loads(text_data)
            message_type = data.get("type")

            if message_type == "message":
                await self.handle_message(data)
            elif message_type == "fetch_chat_history":
                await self.handle_fetch_history(data)
            elif message_type == "mark_as_read":
                await self.handle_mark_as_read(data)
            elif message_type == "typing_start":
                await self.handle_typing_status(True)
            elif message_type == "typing_stop":
                await self.handle_typing_status(False)

        except Exception as e:
            await self.send(text_data=json.dumps({
                "type": "error",
                "message": str(e)
            }))

    async def handle_message(self, data):
        receiver_id = data.get("receiver_id")
        message = data.get("message")

        if not message:
            return

        if self.user:
            # User sends a message to all admins
            chat_message = await self.save_message(self.user.id, None, message, is_admin=False)
            message_data = {
                "type": "chat_message",
                "message": message,
                "id": chat_message.id,
                "sender_id": self.user.id,
                "is_sender_admin": False,
                "timestamp": timezone.now().isoformat(),
                "is_read": False
            }
            receiver_group_name = "admin"
        else:
            # Admin sends a message to a specific user
            chat_message = await self.save_message(self.admin.id, receiver_id, message, is_admin=True)
            message_data = {
                "type": "chat_message",
                "message": message,
                "id": chat_message.id,
                "sender_id": self.admin.id,
                "receiver_id": receiver_id,
                "is_sender_admin": True,
                "timestamp": timezone.now().isoformat(),
                "is_read": False
            }
            receiver_group_name = f"chat_user_{receiver_id}"  # Send to the specific user

        # Send the message to the receiver's group and the sender's group
        await self.channel_layer.group_send(receiver_group_name, {"type": "chat_message", **message_data})
        await self.channel_layer.group_send(self.room_group_name, {"type": "chat_message", **message_data})

    async def handle_fetch_history(self, data):
        user_id = data.get("user_id")
        if user_id:
            chat_history = await self.get_chat_history(user_id)
            await self.send(text_data=json.dumps({
                "type": "chat_history",
                "messages": chat_history
            }))

    async def handle_mark_as_read(self, data):
        if self.admin:
            user_id = data.get("user_id")
            if user_id:
                await self.mark_messages_as_read_by_user(user_id)

    async def handle_typing_status(self, is_typing):
        if self.user:
            # Send typing status to admin group
            await self.channel_layer.group_send("admin", {
                "type": "user_typing",
                "user_id": self.user.id,
                "username": self.user.username,
                "is_typing": is_typing
            })
        elif self.admin and hasattr(self, "current_chat_user_id"):
            await self.channel_layer.group_send(f"chat_user_{self.current_chat_user_id}", {
                "type": "user_typing",
                "is_typing": is_typing
            })

    async def chat_message(self, event):
        # Remove type key as it's used by the channel layer
        message_data = {k: v for k, v in event.items() if k != "type"}
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            **message_data
        }))

    async def user_typing(self, event):
        await self.send(text_data=json.dumps(event))

    @database_sync_to_async
    def mark_messages_as_read_by_user(self, user_id):
        ChatMessage.objects.filter(
            sender_user_id=user_id,
            is_read=False
        ).update(is_read=True)

    @database_sync_to_async
    def get_active_chat_sessions(self):
        sessions = ChatSession.objects.select_related("user").prefetch_related("messages")
        active_sessions = []

        for session in sessions:
            last_message = session.messages.order_by("-timestamp").first()
            unread_count = session.messages.filter(is_read=False, sender_user=session.user).count()

            active_sessions.append({
                "user_id": session.user.id,
                "username": session.user.username,
                "last_message": last_message.message if last_message else "",
                "last_active": session.last_active.isoformat(),
                "unread_count": unread_count,
                "user_image": session.user.user_image
            })

        return sorted(active_sessions, key=lambda x: x["last_active"], reverse=True)

    @database_sync_to_async
    def save_message(self, sender_id, receiver_id, message, is_admin):
        if is_admin:
            sender_admin = Admin.objects.get(id=sender_id)
            receiver_user = User.objects.get(id=receiver_id)
            session, _ = ChatSession.objects.get_or_create(user=receiver_user)
            
            # Update last_active timestamp
            session.last_active = timezone.now()
            session.save()
            
            return ChatMessage.objects.create(
                sender_admin=sender_admin,
                receiver_user=receiver_user,
                message=message,
                session=session,
                timestamp=timezone.now()
            )
        else:
            sender_user = User.objects.get(id=sender_id)
            session, _ = ChatSession.objects.get_or_create(user=sender_user)
            
            # Update last_active timestamp
            session.last_active = timezone.now()
            session.save()
            
            return ChatMessage.objects.create(
                sender_user=sender_user,
                message=message,
                session=session,
                timestamp=timezone.now()
            )

    @database_sync_to_async
    def get_chat_history(self, user_id):
        messages = ChatMessage.objects.filter(
            models.Q(sender_user_id=user_id) | models.Q(receiver_user_id=user_id)
        ).select_related('sender_admin', 'sender_user').order_by("timestamp")

        return [{
            "id": msg.id,
            "message": msg.message,
            "sender_id": msg.sender_admin.id if msg.sender_admin else msg.sender_user.id,
            "is_sender_admin": bool(msg.sender_admin),
            "is_read": msg.is_read,
            "timestamp": msg.timestamp.isoformat()
        } for msg in messages]