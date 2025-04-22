import logging
from datetime import datetime
from .deepseek_service import DeepseekService
from .safety import check_message_safety
from ..models import Message
from ..utils import analyze_sentiment, extract_topics

logger = logging.getLogger(__name__)

def process_user_message(conversation, message_content, user, is_prompt=False):
    """
    Process a user message and get AI response
    
    Args:
        conversation: The Conversation model instance
        message_content: The content of the user's message
        user: The User model instance
        is_prompt: Whether this is a system prompt (bool)
    
    Returns:
        dict: AI response with content and metadata
    """
    try:
        # Check safety first
        is_safe, _ = check_message_safety(message_content)
        if not is_safe and not is_prompt:
            return {
                "content": "I'm sorry, but I cannot respond to that type of content. If you're in crisis, please contact a mental health professional or emergency services.",
                "metadata": {"safety_flagged": True}
            }
        
        # Get conversation history
        messages = prepare_conversation_history(conversation)
        
        # Add the new message
        role = "system" if is_prompt else "user"
        messages.append({
            "role": role,
            "content": message_content
        })
        
        # Get response from AI service
        service = DeepseekService()
        response = service.get_response(messages, user)
        
        # Add sentiment analysis
        sentiment_score = analyze_sentiment(message_content)
        response["sentiment_score"] = sentiment_score
        
        # Add topic extraction
        response["topics"] = extract_topics(message_content)
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing message: {str(e)}")
        return {
            "content": "I apologize, but I'm having trouble processing your message. Could we try again?",
            "metadata": {"error": str(e)}
        }

def prepare_conversation_history(conversation, max_messages=10):
    """
    Prepare conversation history for the AI service
    
    Args:
        conversation: The Conversation model instance
        max_messages: Maximum number of messages to include in history
    
    Returns:
        list: List of message dicts with 'role' and 'content'
    """
    # Get recent messages, excluding system messages
    recent_messages = (
        Message.objects
        .filter(conversation=conversation)
        .exclude(message_type=Message.TYPE_SYSTEM)
        .order_by('-created_at')[:max_messages]
    )
    
    # Reverse to get chronological order
    recent_messages = list(reversed(recent_messages))
    
    # Format for the API
    formatted_messages = []
    for msg in recent_messages:
        role = "assistant" if msg.message_type == Message.TYPE_AI else "user"
        formatted_messages.append({
            "role": role,
            "content": msg.content
        })
    
    return formatted_messages