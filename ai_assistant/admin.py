from django.contrib import admin
from .models import Conversation, Message


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ['id', 'farmer', 'created_at']
    search_fields = ['farmer__username']


@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['conversation', 'role', 'content_preview', 'language', 'timestamp']
    list_filter = ['role', 'language']

    def content_preview(self, obj):
        return obj.content[:60]
    content_preview.short_description = 'Content'
