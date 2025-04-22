from django.contrib import admin
from .models import Conversation, Message, Prompt, ConversationFeedback

@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'user', 'created_at', 'is_active')
    list_filter = ('is_active', 'created_at')
    search_fields = ('title', 'summary', 'user__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at', 'updated_at')

class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ('created_at',)
    
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'message_type', 'short_content', 'created_at', 'flagged_content')
    list_filter = ('message_type', 'flagged_content', 'created_at')
    search_fields = ('content', 'conversation__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)
    
    def short_content(self, obj):
        """Return truncated content for display in admin"""
        return obj.content[:50] + '...' if len(obj.content) > 50 else obj.content
    short_content.short_description = 'Content'

@admin.register(Prompt)
class PromptAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'category', 'is_system', 'use_count')
    list_filter = ('category', 'is_system')
    search_fields = ('title', 'content')
    readonly_fields = ('use_count', 'created_at', 'updated_at')

@admin.register(ConversationFeedback)
class ConversationFeedbackAdmin(admin.ModelAdmin):
    list_display = ('id', 'conversation', 'rating', 'helpful', 'created_at')
    list_filter = ('rating', 'helpful', 'created_at')
    search_fields = ('comments', 'conversation__title')
    date_hierarchy = 'created_at'
    readonly_fields = ('created_at',)