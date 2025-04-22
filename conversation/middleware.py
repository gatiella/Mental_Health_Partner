import time
import logging
from django.utils.deprecation import MiddlewareMixin

logger = logging.getLogger(__name__)

class ConversationMiddleware(MiddlewareMixin):
    """
    Middleware to handle conversation-related tasks and metrics
    """
    
    def process_request(self, request):
        """Process the request before it reaches the view"""
        # Set the start time for the request
        request.start_time = time.time()
        return None
    
    def process_response(self, request, response):
        """Process the response after the view is called"""
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log API call performance for conversation endpoints
            if request.path.startswith('/api/conversation/'):
                logger.info(f"Conversation API call: {request.method} {request.path} "
                            f"completed in {duration:.2f}s with status {response.status_code}")
                
                # Add additional debugging info if there was an error
                if response.status_code >= 400:
                    logger.warning(f"Conversation API error: {request.method} {request.path} "
                                  f"returned {response.status_code}")
        
        return response
    
    def process_exception(self, request, exception):
        """Handle exceptions that occur during processing a request"""
        # Log exception
        logger.error(f"Exception in conversation request: {request.method} {request.path} - {str(exception)}")
        return None