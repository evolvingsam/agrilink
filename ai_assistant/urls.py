from django.urls import path
from .views import ChatView, ConversationHistoryView, NewConversationView, TranscribeVoiceView

urlpatterns = [
    path('chat/', ChatView.as_view(), name='assistant-chat'),
    path('history/<int:conversation_id>/', ConversationHistoryView.as_view(), name='assistant-history'),
    path('new/', NewConversationView.as_view(), name='assistant-new'),
    path('transcribe/', TranscribeVoiceView.as_view(), name='assistant-transcribe'),
]
