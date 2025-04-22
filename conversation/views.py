from rest_framework import viewsets, permissions, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from django.shortcuts import get_object_or_404

from .models import Conversation, Message, Prompt, ConversationFeedback
from .serializers import (
    ConversationListSerializer, ConversationDetailSerializer,
    MessageSerializer, MessageCreateSerializer,
    PromptSerializer, ConversationFeedbackSerializer
)
from .services.conversation import process_user_message
from .services.safety import check_message_safety
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.urls import reverse
from django.http import JsonResponse
from .forms import ConversationForm, MessageForm  # We'll create these forms


@api_view(['GET'])
def conversation_api_root(request, format=None):
    return Response({
        'conversations': reverse('conversation-list', request=request, format=format),
        'messages': reverse('message-list', request=request, format=format),
    })
# Web Views
@login_required
def conversation_list_view(request):
    """Display list of user's conversations"""
    conversations = Conversation.objects.filter(user=request.user).order_by('-updated_at')
    return render(request, 'conversation/conversation_list.html', {
        'conversations': conversations
    })

@login_required
def conversation_detail_view(request, pk):
    """Display a single conversation with messages"""
    conversation = get_object_or_404(Conversation, pk=pk, user=request.user)
    messages_list = Message.objects.filter(conversation=conversation).order_by('created_at')
    message_form = MessageForm()
    
    if request.method == 'POST':
        message_form = MessageForm(request.POST)
        if message_form.is_valid():
            user_message_content = message_form.cleaned_data['content']
            
            # Create user message
            user_message = Message.objects.create(
                conversation=conversation,
                message_type=Message.TYPE_USER,
                content=user_message_content
            )
            
            # Process message and get AI response (reusing your existing service)
            ai_response = process_user_message(conversation, user_message_content, request.user)
            
            # Create AI message
            ai_message = Message.objects.create(
                conversation=conversation,
                message_type=Message.TYPE_AI,
                content=ai_response['content'],
                metadata=ai_response.get('metadata', {})
            )
            
            # For AJAX requests, return JSON response
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({
                    'user_message': {
                        'id': user_message.id,
                        'content': user_message.content,
                        'created_at': user_message.created_at.isoformat()
                    },
                    'ai_message': {
                        'id': ai_message.id,
                        'content': ai_message.content,
                        'created_at': ai_message.created_at.isoformat()
                    }
                })
            
            # For regular POST requests, redirect to avoid resubmission
            return redirect('web-conversation-detail', pk=pk)
    
    return render(request, 'conversation/conversation_detail.html', {
        'conversation': conversation,
        'messages': messages_list,
        'form': message_form
    })

@login_required
def conversation_create_view(request):
    """Create a new conversation"""
    if request.method == 'POST':
        form = ConversationForm(request.POST)
        if form.is_valid():
            conversation = form.save(commit=False)
            conversation.user = request.user
            conversation.save()
            
            messages.success(request, 'Conversation created successfully!')
            return redirect('web-conversation-detail', pk=conversation.id)
    else:
        form = ConversationForm()
    
    return render(request, 'conversation/conversation_form.html', {
        'form': form,
        'title': 'Start New Conversation'
    })

@login_required
def prompt_list_view(request):
    """Display available prompts"""
    prompts = Prompt.objects.filter(is_system=False)
    return render(request, 'conversation/prompt_list.html', {
        'prompts': prompts
    })

@login_required
def use_prompt_view(request, pk):
    """Use a prompt in a conversation"""
    prompt = get_object_or_404(Prompt, pk=pk)
    conversation_id = request.POST.get('conversation')
    
    if conversation_id:
        conversation = get_object_or_404(Conversation, id=conversation_id, user=request.user)
        
        if not conversation.is_active:
            messages.error(request, 'This conversation has ended. Please start a new one.')
            return redirect('web-conversation-list')
        
        # Increment prompt usage
        prompt.use_count += 1
        prompt.save()
        
        # Create system message
        system_message = Message.objects.create(
            conversation=conversation,
            message_type=Message.TYPE_SYSTEM,
            content=prompt.content
        )
        
        # Process the prompt
        ai_response = process_user_message(conversation, prompt.content, request.user, is_prompt=True)
        
        # Create AI message
        Message.objects.create(
            conversation=conversation,
            message_type=Message.TYPE_AI,
            content=ai_response['content'],
            metadata=ai_response.get('metadata', {})
        )
        
        messages.success(request, f'Prompt "{prompt.title}" applied successfully.')
        return redirect('web-conversation-detail', pk=conversation.id)
    
    # If no conversation selected or failed, show error
    messages.error(request, 'Please select a valid conversation.')
    return redirect('web-prompt-list')
    
    
    
class ConversationViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    """
    API endpoint for managing conversations
    """
    serializer_class = ConversationListSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['title', 'summary', 'topics']
    ordering_fields = ['created_at', 'updated_at']
    
    def get_queryset(self):
        """Only return conversations belonging to the current user"""
        return Conversation.objects.filter(user=self.request.user)
    
    def get_serializer_class(self):
        if self.action == 'retrieve' or self.action == 'update':
            return ConversationDetailSerializer
        return ConversationListSerializer
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def end_conversation(self, request, pk=None):
        """End an active conversation"""
        conversation = self.get_object()
        if not conversation.is_active:
            return Response(
                {"error": "This conversation is already ended."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        conversation.is_active = False
        conversation.ended_at = timezone.now()
        conversation.save()
        
        return Response({"message": "Conversation ended successfully."})
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        """Send a message in a conversation and get AI response"""
        conversation = self.get_object()
        
        if not conversation.is_active:
            return Response(
                {"error": "This conversation has ended. Please start a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create user message
        serializer = MessageCreateSerializer(data={
            'conversation': conversation.id,
            'message_type': Message.TYPE_USER,
            'content': request.data.get('content', '')
        })
        serializer.is_valid(raise_exception=True)
        user_message = serializer.save()
        
        # Safety check
        is_safe, flag_reason = check_message_safety(user_message.content)
        if not is_safe:
            user_message.flagged_content = True
            user_message.flag_reason = flag_reason
            user_message.save()
            
            return Response({
                "error": "Your message was flagged for safety concerns.",
                "reason": flag_reason,
                "message": user_message.id
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Process message and get AI response
        ai_response = process_user_message(conversation, user_message.content, request.user)
        
        # Create AI message in database
        ai_message = Message.objects.create(
            conversation=conversation,
            message_type=Message.TYPE_AI,
            content=ai_response['content'],
            metadata=ai_response.get('metadata', {})
        )
        
        # Update conversation if needed
        if 'sentiment_score' in ai_response:
            conversation.sentiment_score = ai_response['sentiment_score']
        
        if 'topics' in ai_response and ai_response['topics']:
            # Append new topics
            existing_topics = set(conversation.topics)
            for topic in ai_response['topics']:
                existing_topics.add(topic)
            conversation.topics = list(existing_topics)
        
        conversation.save()
        
        # Return both messages
        return Response({
            'user_message': MessageSerializer(user_message).data,
            'ai_message': MessageSerializer(ai_message).data
        })
    
    @action(detail=True, methods=['post'])
    def provide_feedback(self, request, pk=None):
        """Allow users to provide feedback on a conversation"""
        conversation = self.get_object()
        
        serializer = ConversationFeedbackSerializer(data={
            'conversation': conversation.id,
            'rating': request.data.get('rating'),
            'helpful': request.data.get('helpful'),
            'comments': request.data.get('comments', '')
        })
        serializer.is_valid(raise_exception=True)
        feedback = serializer.save()
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class MessageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing messages (read-only)
    """
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Only allow access to messages from user's conversations"""
        return Message.objects.filter(conversation__user=self.request.user)
    
    @action(detail=True, methods=['post'])
    def flag(self, request, pk=None):
        """Flag inappropriate messages"""
        message = self.get_object()
        
        if message.conversation.user != request.user:
            return Response(
                {"error": "You don't have permission to flag this message."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        message.flagged_content = True
        message.flag_reason = request.data.get('reason', 'User flagged content')
        message.save()
        
        return Response({"message": "Content flagged successfully."})

class PromptViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for viewing available prompts (read-only)
    """
    queryset = Prompt.objects.filter(is_system=False)  # Only show non-system prompts
    serializer_class = PromptSerializer
    permission_classes = [permissions.IsAuthenticated]
    filter_backends = [filters.SearchFilter]
    search_fields = ['title', 'content', 'category']
    
    @action(detail=True, methods=['post'])
    def use(self, request, pk=None):
        """Use a prompt in a conversation"""
        prompt = self.get_object()
        conversation_id = request.data.get('conversation')
        
        if not conversation_id:
            return Response(
                {"error": "Conversation ID is required"},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get the conversation and make sure it belongs to the user
        conversation = get_object_or_404(Conversation, id=conversation_id)
        if conversation.user != request.user:
            return Response(
                {"error": "You don't have permission to use this conversation."},
                status=status.HTTP_403_FORBIDDEN
            )
        
        if not conversation.is_active:
            return Response(
                {"error": "This conversation has ended. Please start a new one."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Increment prompt usage
        prompt.use_count += 1
        prompt.save()
        
        # Create system message
        system_message = Message.objects.create(
            conversation=conversation,
            message_type=Message.TYPE_SYSTEM,
            content=prompt.content
        )
        
        # Process the prompt and get AI response
        ai_response = process_user_message(conversation, prompt.content, request.user, is_prompt=True)
        
        # Create AI message
        ai_message = Message.objects.create(
            conversation=conversation,
            message_type=Message.TYPE_AI,
            content=ai_response['content'],
            metadata=ai_response.get('metadata', {})
        )
        
        return Response({
            'system_message': MessageSerializer(system_message).data,
            'ai_message': MessageSerializer(ai_message).data
        })