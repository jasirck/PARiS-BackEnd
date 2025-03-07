# messege/models.py
from django.db import models
from django.utils.timezone import now
from rest_framework.exceptions import ValidationError

from users.models import User
from admin_user.models import Admin


class ChatMessage(models.Model):
    sender_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    sender_admin = models.ForeignKey(
        Admin,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="sent_messages",
    )
    receiver_user = models.ForeignKey(
        User,
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name="received_messages",
    )
    message = models.TextField()
    session = models.ForeignKey(
        "ChatSession", on_delete=models.CASCADE, related_name="messages"
    )
    timestamp = models.DateTimeField(default=now)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        if self.sender_user:
            return (
                f"From User {self.sender_user.username} to Admins: {self.message[:20]}"
            )
        else:
            return f"From Admin {self.sender_admin.username} to User {self.receiver_user.username}: {self.message[:20]}"

    def clean(self):
        if not (self.sender_user or self.sender_admin):
            raise ValidationError(
                "A message must have a sender (either user or admin)."
            )
        if self.sender_user and self.sender_admin:
            raise ValidationError(
                "A message cannot have both a user and an admin as the sender."
            )
        if self.sender_admin and not self.receiver_user:
            raise ValidationError("An admin's message must have a receiver_user.")
        if self.sender_user and self.receiver_user:
            raise ValidationError(
                "A user's message cannot have a receiver_user (it goes to all admins)."
            )


class ChatSession(models.Model):
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="chat_sessions"
    )
    last_active = models.DateTimeField(default=now)

    def __str__(self):
        return f"Chat session for {self.user.username}"
