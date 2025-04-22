from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.utils import timezone
from .models import Conversation, Message, ConversationFeedback
from .utils import analyze_sentiment, extract_topics, generate_conversation_summary, log_conversation_metrics

@receiver(post_save, sender=Message)
def update_conversation_after_message(sender, instance, created, **kwargs):
    """Update conversation metadata when a new message is added"""
    if created:
        conversation = instance.conversation
        
        # Update last activity timestamp
        conversation.updated_at = timezone.now()
        
        # Update conversation title if it's empty and this is one of the first messages
        if not conversation.title and conversation.messages.count() <= 2:
            # Only do this for user messages
            if instance.message_type == 'user':
                # Use the first 5-8 words as a title
                words = instance.content.split()[:8]
                title = ' '.join(words)
                
                # Truncate if too long
                if len(title) > 50:
                    title = title[:47] + "..."
                    
                conversation.title = title
        
        # If this is a user message, analyze sentiment and topics
        if instance.message_type == 'user':
            # Analyze sentiment
            instance.sentiment_score = analyze_sentiment(instance.content)
            instance.save(update_fields=['sentiment_score'])
            
            # Extract topics
            new_topics = extract_topics(instance.content)
            if new_topics:
                existing_topics = set(conversation.topics)
                for topic in new_topics:
                    existing_topics.add(topic)
                conversation.topics = list(existing_topics)
            
            # If it's the first message, set the mood_start
            if conversation.messages.filter(message_type='user').count() == 1:
                sentiment_score = instance.sentiment_score
                
                if sentiment_score >= 0.5:
                    conversation.mood_start = 'positive'
                elif sentiment_score <= -0.3:
                    conversation.mood_start = 'negative'
                else:
                    conversation.mood_start = 'neutral'
        
        # Save the conversation
        conversation.save()

@receiver(post_save, sender=ConversationFeedback)
def handle_conversation_feedback(sender, instance, created, **kwargs):
    """Process conversation feedback"""
    if created:
        # You could implement additional processing here
        # For example, notify admins about negative feedback
        if instance.rating and instance.rating <= 2:
            # In a real app, you might want to send an alert
            pass

@receiver(post_save, sender=Conversation)
def generate_summary_when_ended(sender, instance, created, **kwargs):
    """Generate a summary when a conversation is ended"""
    if not created and not instance.is_active and instance.ended_at:
        # Check if summary is empty
        if not instance.summary:
            messages = instance.messages.all()
            instance.summary = generate_conversation_summary(messages)
            
            # Set mood_end based on recent messages
            user_messages = instance.messages.filter(message_type='user').order_by('-created_at')[:3]
            if user_messages:
                # Calculate average sentiment of last few messages
                sentiment_scores = [m.sentiment_score for m in user_messages if m.sentiment_score is not None]
                if sentiment_scores:
                    avg_sentiment = sum(sentiment_scores) / len(sentiment_scores)
                    
                    if avg_sentiment >= 0.5:
                        instance.mood_end = 'positive'
                    elif avg_sentiment <= -0.3:
                        instance.mood_end = 'negative'
                    else:
                        instance.mood_end = 'neutral'
            
            # Save without triggering this signal again
            Conversation.objects.filter(id=instance.id).update(
                summary=instance.summary,
                mood_end=instance.mood_end
            )
            
            # Log metrics
            log_conversation_metrics(instance)