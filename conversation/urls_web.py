from django.urls import path
from . import views

urlpatterns = [
    path('', views.conversation_list_view, name='web-conversation-list'),
    path('new/', views.conversation_create_view, name='web-conversation-create'),
    path('<int:pk>/', views.conversation_detail_view, name='web-conversation-detail'),
    path('prompts/', views.prompt_list_view, name='web-prompt-list'),
    path('prompts/<int:pk>/use/', views.use_prompt_view, name='web-use-prompt'),
]