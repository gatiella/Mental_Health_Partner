from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ConversationViewSet, MessageViewSet, PromptViewSet
from . import views

router = DefaultRouter()
router.register(r'', ConversationViewSet, basename='conversation')
#router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'prompts', PromptViewSet, basename='prompt')

urlpatterns = [
    path('', include(router.urls)),
    path('', views.conversation_api_root, name='conversation-api-root'),
    
]
