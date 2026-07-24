from rest_framework import serializers
from .models import Conversation, Message


class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'role', 'content', 'language', 'timestamp']
        read_only_fields = fields


class ConversationSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    farmer_name = serializers.CharField(source='farmer.username', read_only=True)

    class Meta:
        model = Conversation
        fields = ['id', 'farmer_name', 'created_at', 'messages']
        read_only_fields = fields


class ChatInputSerializer(serializers.Serializer):
    """Validates the body of POST /api/assistant/chat/"""
    message = serializers.CharField(required=True, max_length=2000)
    conversation_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Omit to start a new conversation.',
    )
    language = serializers.CharField(
        required=False,
        default='en',
        max_length=10,
    )
