import requests
import logging
from django.conf import settings

logger = logging.getLogger(__name__)

class DeepseekService:
    """Service for interacting with Deepseek via OpenRouter"""
    
    def __init__(self):
        self.api_key = settings.DEEPSEEK_API_KEY
        self.api_url = "https://openrouter.ai/api/v1"
        self.model_name = "deepseek/deepseek-chat-v3-0324:free"  
        self.site_url = getattr(settings, 'SITE_URL', 'http://localhost:8000')
        
        if not self.api_key:
            logger.warning("OpenRouter API key is not set. Using mock responses.")
    
    def get_response(self, messages, user=None):
        """Get response from Deepseek via OpenRouter"""
        if not self.api_key:
            return self._mock_response(messages)
        
        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": self.site_url,
                "X-Title": "Mental Health Partner",
                "Content-Type": "application/json"
            }
            
            system_message = {
                "role": "system",
                "content": self._get_system_prompt(user)
            }
            
            
            # Maintain conversation context with last 5 exchanges
            context_messages = self._get_context_messages(messages, system_message)
            
            payload = {
                "model": self.model_name,
                "messages": context_messages,
                "temperature": 0.7,
                "max_tokens": 350,
                "top_p": 0.9,
                "frequency_penalty": 0.2,
                "presence_penalty": 0.2
            }
            
            logger.debug(f"Sending payload to OpenRouter: {payload}")
            
            response = requests.post(
                f"{self.api_url}/chat/completions",
                headers=headers,
                json=payload,
                timeout=20
            )
            
            response.raise_for_status()
            data = response.json()
            logger.debug(f"Received API response: {data}")
            
            return {
            "content": data["choices"][0]["message"]["content"].strip(),
            "metadata": {
                "model": data.get("model", self.model_name),
                "usage": data.get("usage", {}),  # Use get() with default empty dict
                "finish_reason": data.get("choices", [{}])[0].get("finish_reason", "unknown")
            }
        }
            
        except requests.exceptions.HTTPError as e:
            error_msg = f"HTTP Error {e.response.status_code}: {e.response.text}"
            logger.error(error_msg)
            
            # User-friendly error messages
            if e.response.status_code == 401:
                return self._auth_error_response()
            elif e.response.status_code == 429:
                return self._rate_limit_response()
            else:
                return self._generic_error_response()
                
        except Exception as e:
            logger.error(f"General error: {str(e)}", exc_info=True)
            return self._mock_response(messages)

    def _get_system_prompt(self, user=None):
        """Optimized system prompt with clinical safeguards"""
        prompt = """You are an empathetic mental health supporter. Guidelines:
1. Use active listening and validation techniques
2. Ask open-ended questions to understand deeper
3. Suggest coping strategies when appropriate
4. Never diagnose conditions
5. Encourage professional help if needed
6. Responses must be concise (150-300 words)
7. Use simple, clear language
8. If crisis detected, provide emergency contacts

Example response: "That sounds challenging. What emotions are coming up for you?"""
        
        if user and hasattr(user, 'preferences'):
            try:
                if user.preferences.get('communication_style'):
                    prompt += f"\nCommunication style: {user.preferences['communication_style']}"
                if user.preferences.get('topics'):
                    topics = ", ".join(user.preferences['topics'])
                    prompt += f"\nRelevant topics: {topics}"
            except Exception as e:
                logger.error(f"Error loading preferences: {str(e)}")
        
        return prompt

    def _get_context_messages(self, messages, system_message):
        """Maintain conversation context within token limits"""
        max_context = 8  # Keep last 4 exchanges (user+assistant pairs)
        return [system_message] + messages[-max_context:]

    def _auth_error_response(self):
        return {
            "content": "Authentication issue with conversation service. Please try again later.",
            "metadata": {"error": "API authentication failed"}
        }

    def _rate_limit_response(self):
        return {
            "content": "I'm getting too many requests right now. Please wait a moment and try again.",
            "metadata": {"error": "Rate limit exceeded"}
        }

    def _generic_error_response(self):
        return {
            "content": "Temporary issue with conversation service. Please try again.",
            "metadata": {"error": "General API error"}
        }

    def _mock_response(self, messages):
        """Enhanced mock responses with context awareness"""
        last_message = messages[-1]["content"].lower() if messages else ""
        
        responses = {
            'sad': "I hear you're feeling down. Would you like to share more about what's been on your mind?",
            'anxious': "Anxiety can feel overwhelming. Let's try a grounding exercise: name 3 things you can hear right now.",
            'angry': "Anger is a valid emotion. What's been happening that's brought up these feelings?",
            'happy': "That's wonderful! What positive experiences have contributed to this mood?",
            'default': "Thank you for sharing. Could you tell me more about how this has affected you?"
        }
        
        for key in responses:
            if key in last_message:
                return {"content": responses[key], "metadata": {"mock": True}}
                
        return {"content": responses['default'], "metadata": {"mock": True}}