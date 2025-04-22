import re
import logging

logger = logging.getLogger(__name__)

# List of potentially concerning patterns
CONCERNING_PATTERNS = [
    (r'\b(kill|harm|hurt)(ing)?\s+(my)?self\b', 'self-harm'),
    (r'\b(suicide|suicidal|end my life)\b', 'suicide'),
    (r'\b(want|going|plan)\s+to\s+die\b', 'suicide'),
    (r'\b(kill|murder|hurt|harm)\s+(others|people|someone|them)\b', 'harm to others'),
    (r'\bdrugs?\b', 'substance abuse'),
    (r'\balcohol\b', 'substance abuse'),
    (r'\boverdose\b', 'substance abuse'),
    (r'\b(abuse|abusing|abused)\b', 'abuse'),
    (r'\b(emergency|crisis|urgent)\b', 'crisis'),
]

# List of emergency keywords that should trigger immediate response
EMERGENCY_KEYWORDS = [
    'suicide', 'kill myself', 'end my life', 'want to die', 
    'hurt myself', 'self-harm', 'cutting myself', 'emergency'
]

def check_message_safety(message_content):
    """
    Check message content for safety concerns
    
    Args:
        message_content: The content of the user's message
        
    Returns:
        tuple: (is_safe, flag_reason)
    """
    try:
        # Convert to lowercase for case-insensitive matching
        content_lower = message_content.lower()
        
        # Check for emergency patterns first
        for keyword in EMERGENCY_KEYWORDS:
            if keyword in content_lower:
                logger.warning(f"Emergency keyword detected: {keyword}")
                return False, f"Emergency keyword detected: {keyword}"
        
        # Check for concerning patterns
        for pattern, category in CONCERNING_PATTERNS:
            if re.search(pattern, content_lower):
                # This is concerning but not necessarily unsafe
                logger.info(f"Concerning pattern detected: {category}")
                # We don't block the message, but we flag it
                return True, f"Concerning pattern detected: {category}"
        
        # If no pattern matched, the message is safe
        return True, ""
        
    except Exception as e:
        logger.error(f"Error in safety check: {str(e)}")
        # Default to safe if there's an error in the safety check
        return True, ""

def get_crisis_resources():
    """
    Get a list of crisis resources
    
    Returns:
        str: Formatted crisis resources
    """
    return """
    If you're experiencing a mental health crisis, please consider these resources:
    
    - National Suicide Prevention Lifeline: 1-800-273-8255
    - Crisis Text Line: Text HOME to 741741
    - Emergency Services: 911 (US) or your local emergency number
    - International Association for Suicide Prevention: https://www.iasp.info/resources/Crisis_Centres/
    
    Remember, it's okay to ask for help, and people care about you.
    """