from rest_framework import serializers
from .models import Conversation, Message, Prompt, ConversationFeedback

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'message_type', 'content', 'sentiment_score', 
                  'metadata', 'flagged_content', 'flag_reason', 'created_at']
        read_only_fields = ['id', 'sentiment_score', 'flagged_content', 
                           'flag_reason', 'created_at']

class ConversationListSerializer(serializers.ModelSerializer):
    message_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'summary', 'created_at', 'updated_at', 
                  'is_active', 'mood_start', 'mood_end', 'message_count']
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_message_count(self, obj):
        return obj.messages.count()

class ConversationDetailSerializer(serializers.ModelSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['id', 'title', 'summary', 'created_at', 'updated_at', 
                  'ended_at', 'is_active', 'mood_start', 'mood_end', 
                  'sentiment_score', 'topics', 'messages']
        read_only_fields = ['id', 'created_at', 'updated_at', 'sentiment_score']

class MessageCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['conversation', 'message_type', 'content']
    
    def validate_message_type(self, value):
        if value not in [Message.TYPE_USER, Message.TYPE_SYSTEM]:
            raise serializers.ValidationError("Only user and system messages can be created directly.")
        return value

class PromptSerializer(serializers.ModelSerializer):
    class Meta:
        model = Prompt
        fields = ['id', 'title', 'content', 'category', 'is_system', 
                  'trigger_conditions', 'use_count', 'created_at', 'updated_at']
        read_only_fields = ['id', 'use_count', 'created_at', 'updated_at']

class ConversationFeedbackSerializer(serializers.ModelSerializer):
    class Meta:
        model = ConversationFeedback
        fields = ['id', 'conversation', 'rating', 'helpful', 'comments', 'created_at']
        read_only_fields = ['id', 'created_at']