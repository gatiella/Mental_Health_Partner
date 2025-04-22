from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def send_welcome_email(user):
    """Send welcome email to new users"""
    try:
        subject = "Welcome to Mental Health Partner"
        message = f"""
        Hello {user.first_name},
        
        Welcome to Mental Health Partner! We're glad you've joined us on this journey towards better mental health.
        
        Get started by setting up your profile and preferences.
        
        Best regards,
        The Mental Health Partner Team
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [user.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        logger.error(f"Failed to send welcome email to {user.email}: {str(e)}")
        return False

def generate_user_analytics(user):
    """Generate basic analytics for a user"""
    from conversation.models import Conversation, Message
    
    # Get user conversations
    conversations = Conversation.objects.filter(user=user)
    conversation_count = conversations.count()
    
    # Get user messages
    messages = Message.objects.filter(conversation__user=user)
    message_count = messages.count()
    
    # Calculate average messages per conversation
    avg_messages = message_count / conversation_count if conversation_count > 0 else 0
    
    return {
        'conversation_count': conversation_count,
        'message_count': message_count,
        'avg_messages_per_conversation': avg_messages,
        'last_conversation': conversations.order_by('-created_at').first().created_at if conversation_count > 0 else None,
    }