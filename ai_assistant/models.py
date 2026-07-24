from django.db import models
from django.conf import settings


class Conversation(models.Model):
    """A conversation session between a farmer and the AI assistant."""
    farmer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations',
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f'Conversation #{self.id} — {self.farmer.username}'


class Message(models.Model):
    """A single message in a conversation."""

    class Role(models.TextChoices):
        FARMER = 'farmer', 'Farmer'
        ASSISTANT = 'assistant', 'Assistant'

    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages',
    )
    role = models.CharField(max_length=10, choices=Role.choices)
    content = models.TextField()
    language = models.CharField(max_length=10, default='en')
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f'[{self.role}] {self.content[:60]}'
