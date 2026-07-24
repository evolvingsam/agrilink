from rest_framework import permissions
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Conversation
from .serializers import ChatInputSerializer, ConversationSerializer
from .service import chat


class ChatView(APIView):
    """
    POST /api/assistant/chat/
    Send a text message to the AI assistant.
    Optionally pass conversation_id to continue a session;
    omit it to start a new conversation.

    Body:
        {
            "message": "I wan sell 50kg of tomato",
            "conversation_id": 3,   (optional)
            "language": "en"        (optional, default: "en")
        }
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = ChatInputSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        user = request.user

        # Get or create conversation
        conv_id = data.get('conversation_id')
        if conv_id:
            conversation = get_object_or_404(Conversation, pk=conv_id, farmer=user)
        else:
            conversation = Conversation.objects.create(farmer=user)

        result = chat(conversation, data['message'], user)

        return Response({
            'conversation_id': conversation.id,
            'reply': result['reply'],
            'action_result': result['action_result'],
        })


class ConversationHistoryView(APIView):
    """
    GET /api/assistant/history/<conversation_id>/
    Returns all messages in a conversation (farmer must own it).
    """
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, conversation_id):
        conversation = get_object_or_404(
            Conversation, pk=conversation_id, farmer=request.user
        )
        serializer = ConversationSerializer(conversation)
        return Response(serializer.data)


class NewConversationView(APIView):
    """
    POST /api/assistant/new/
    Explicitly start a new conversation session and return its ID.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        conversation = Conversation.objects.create(farmer=request.user)
        return Response({'conversation_id': conversation.id})

class TranscribeVoiceView(APIView):
    """
    POST /api/assistant/transcribe/
    Expects multipart/form-data with an 'audio' file.
    Transcribes the audio and returns the text in English.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        audio_file = request.FILES.get('audio')
        if not audio_file:
            return Response({'error': 'No audio file provided'}, status=400)
            
        from .service import transcribe_audio
        try:
            transcription = transcribe_audio(audio_file)
            return Response({'text': transcription})
        except Exception as e:
            return Response({'error': str(e)}, status=500)
