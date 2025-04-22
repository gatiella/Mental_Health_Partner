from django.db import models
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class Conversation(models.Model):
    """Model representing a conversation session between user and AI"""
    
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='conversations'
    )
    
    title = models.CharField(max_length=200, blank=True)
    summary = models.TextField(blank=True)
    
    # Conversation metadata
    mood_start = models.CharField(max_length=50, blank=True)
    mood_end = models.CharField(max_length=50, blank=True)
    
    sentiment_score = models.FloatField(null=True, blank=True)
    topics = models.JSONField(default=list, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    ended_at = models.DateTimeField(null=True, blank=True)
    
    # Status
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.title or 'Untitled'} - {self.user.username}"
    
    class Meta:
        ordering = ['-updated_at']

class Message(models.Model):
    """Model representing a message in a conversation"""
    
    TYPE_USER = 'user'
    TYPE_AI = 'ai'
    TYPE_SYSTEM = 'system'
    
    MESSAGE_TYPES = [
        (TYPE_USER, _('User')),
        (TYPE_AI, _('AI')),
        (TYPE_SYSTEM, _('System')),
    ]
    
    conversation = models.ForeignKey(
        Conversation,
        on_delete=models.CASCADE,
        related_name='messages'
    )
    
    message_type = models.CharField(
        max_length=10,
        choices=MESSAGE_TYPES,
        default=TYPE_USER
    )
    
    content = models.TextField()
    sentiment_score = models.FloatField(null=True, blank=True)
    
    # Message metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    # Safety flags
    flagged_content = models.BooleanField(default=False)
    flag_reason = models.CharField(max_length=200, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.message_type}: {self.content[:50]}..."
    
    class Meta:
        ordering = ['created_at']

class Prompt(models.Model):
    """Model for storing system prompts for the AI assistant"""
    
    CATEGORY_CHOICES = [
        ('general', _('General')),
        ('crisis', _('Crisis')),
        ('therapy', _('Therapy')),
        ('motivation', _('Motivation')),
        ('reflection', _('Reflection')),
    ]
    
    title = models.CharField(max_length=100)
    content = models.TextField()
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='general')
    
    # For system use (e.g., automatically triggered by user sentiment)
    is_system = models.BooleanField(default=False)
    trigger_conditions = models.JSONField(default=dict, blank=True)
    
    # For tracking usage
    use_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.title} ({self.category})"
    
    class Meta:
        ordering = ['category', 'title']

class ConversationFeedback(models.Model):
    """Model for storing user feedback on conversations"""
    
    conversation = models.ForeignKey(
        Conversation, 
        on_delete=models.CASCADE,
        related_name='feedback'
    )
    
    rating = models.IntegerField(
        choices=[(1, '1'), (2, '2'), (3, '3'), (4, '4'), (5, '5')],
        null=True,
        blank=True
    )
    
    helpful = models.BooleanField(null=True, blank=True)
    comments = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Feedback for {self.conversation}"