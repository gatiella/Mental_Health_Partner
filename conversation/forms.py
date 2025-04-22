from django import forms
from .models import Conversation, Message

class ConversationForm(forms.ModelForm):
    """Form for creating/editing a conversation"""
    class Meta:
        model = Conversation
        fields = ['title', 'summary']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class MessageForm(forms.Form):
    """Form for sending a message"""
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 3,
            'placeholder': 'Type your message here...'
        }),
        label=''
    )