import re
import logging
import json
from django.conf import settings

logger = logging.getLogger(__name__)

def analyze_sentiment(text):
    """
    Basic sentiment analysis of text.
    Returns a sentiment score from -1.0 (negative) to 1.0 (positive).
    """
    # This is a simplified version - in production you might use a more sophisticated approach
    # or a third-party API/service
    
    # Lists of positive and negative words
    positive_words = [
        'good', 'great', 'happy', 'better', 'best', 'excellent', 'wonderful', 'amazing',
        'love', 'enjoy', 'pleased', 'positive', 'awesome', 'fantastic', 'delighted',
        'glad', 'thankful', 'grateful', 'satisfied', 'exciting', 'hope', 'peaceful'
    ]
    
    negative_words = [
        'bad', 'worst', 'sad', 'terrible', 'awful', 'horrible', 'negative', 'poor',
        'hate', 'dislike', 'angry', 'upset', 'depressed', 'disappointed', 'unhappy',
        'stressed', 'anxious', 'afraid', 'worried', 'sorry', 'alone', 'hopeless'
    ]
    
    # Convert to lowercase and remove punctuation
    text_cleaned = re.sub(r'[^\w\s]', '', text.lower())
    words = text_cleaned.split()
    
    positive_count = sum(1 for word in words if word in positive_words)
    negative_count = sum(1 for word in words if word in negative_words)
    
    total_words = len(words)
    if total_words == 0:
        return 0
    
    # Calculate sentiment score between -1 and 1
    return (positive_count - negative_count) / total_words
    
def extract_topics(text):
    """
    Extract potential topics from conversation text
    Returns a list of topic keywords
    """
    # This is a simplified version - in production you might use NLP techniques
    
    # Common mental health topics
    topic_keywords = {
        'anxiety': ['anxiety', 'anxious', 'worry', 'panic', 'fear', 'stressed'],
        'depression': ['depression', 'depressed', 'sad', 'hopeless', 'unmotivated'],
        'relationships': ['relationship', 'partner', 'friend', 'family', 'marriage', 'divorce'],
        'self-esteem': ['confidence', 'self-esteem', 'self-worth', 'value', 'validation'],
        'grief': ['grief', 'loss', 'death', 'died', 'mourning', 'bereavement'],
        'stress': ['stress', 'overwhelmed', 'pressure', 'burnout', 'workload'],
        'trauma': ['trauma', 'traumatic', 'abuse', 'ptsd', 'flashback'],
        'sleep': ['sleep', 'insomnia', 'nightmare', 'tired', 'fatigue'],
        'anger': ['anger', 'angry', 'rage', 'frustration', 'irritable'],
        'addiction': ['addiction', 'addicted', 'substance', 'alcohol', 'drug', 'gambling'],
    }
    
    # Convert to lowercase
    text_lower = text.lower()
    
    # Find topics
    found_topics = []
    for topic, keywords in topic_keywords.items():
        if any(keyword in text_lower for keyword in keywords):
            found_topics.append(topic)
    
    return found_topics

def generate_conversation_summary(messages):
    """
    Generate a brief summary of a conversation based on the messages
    """
    if not messages:
        return "No messages in conversation"
    
    # Get user messages only
    user_messages = [m.content for m in messages if m.message_type == 'user']
    
    if not user_messages:
        return "No user messages in conversation"
    
    # Concatenate the first message and last message if they're different
    if len(user_messages) == 1:
        summary = user_messages[0][:100]
    else:
        first_msg = user_messages[0][:50]
        last_msg = user_messages[-1][:50]
        
        if first_msg != last_msg:
            summary = f"{first_msg}... {last_msg}"
        else:
            summary = first_msg
    
    # Truncate if needed
    if len(summary) > 100:
        summary = summary[:97] + "..."
    
    return summary

def log_conversation_metrics(conversation):
    """
    Log metrics about a conversation for monitoring and analysis
    """
    try:
        messages = conversation.messages.all()
        user_messages = [m for m in messages if m.message_type == 'user']
        ai_messages = [m for m in messages if m.message_type == 'ai']
        
        metrics = {
            'conversation_id': conversation.id,
            'user_id': conversation.user.id,
            'total_messages': len(messages),
            'user_messages': len(user_messages),
            'ai_messages': len(ai_messages),
            'duration_minutes': (conversation.ended_at - conversation.created_at).total_seconds() / 60 
                if conversation.ended_at else None,
            'sentiment_score': conversation.sentiment_score,
            'topics': conversation.topics
        }
        
        logger.info(f"Conversation metrics: {json.dumps(metrics)}")
        return metrics
    
    except Exception as e:
        logger.error(f"Error logging conversation metrics: {str(e)}")
        return None