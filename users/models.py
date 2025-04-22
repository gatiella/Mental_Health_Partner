from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class CustomUser(AbstractUser):
    """Custom user model extending Django's built-in User"""
    
    profile_picture = models.ImageField(
        upload_to='profile_pictures/',
        default='default-profile.png',  # Add default image
        null=True,
        blank=True
    )
    groups = models.ManyToManyField(
        'auth.Group',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
        help_text='The groups this user belongs to.',
        verbose_name='groups'
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        related_name='custom_user_set',
        related_query_name='custom_user',
        blank=True,
        help_text='Specific permissions for this user.',
        verbose_name='user permissions'
    )
    
    # Additional fields
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = models.ImageField(upload_to='profile_pictures/', null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Mental health related fields
    mental_health_history = models.TextField(blank=True)
    emergency_contact_name = models.CharField(max_length=100, blank=True)
    emergency_contact_phone = models.CharField(max_length=20, blank=True)
    
    # Preferences
    notification_preferences = models.JSONField(default=dict, blank=True)
    therapy_preferences = models.JSONField(default=dict, blank=True)
    
    def __str__(self):
        return self.username

class UserPreference(models.Model):
    """Store user preferences for the mental health partner app"""
    RESPONSE_LENGTH_CHOICES = [
        ('short', 'Short'),
        ('medium', 'Medium'),
        ('long', 'Long'),
    ]
    
    CONVERSATION_STYLE_CHOICES = [
        ('supportive', 'Supportive'),
        ('directive', 'Directive'),
        ('analytical', 'Analytical'),
        ('empathetic', 'Empathetic'),
    ]
    
    THEME_CHOICES = [
        ('light', 'Light'),
        ('dark', 'Dark'),
        ('system', 'System Default'),
    ]
    
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='preferences')
    
    # AI conversation preferences
    ai_response_length = models.CharField(
        max_length=10,
        choices=[
            ('short', 'Short'),
            ('medium', 'Medium'),
            ('long', 'Long'),
        ],
        default='medium'
    )
    
    conversation_style = models.CharField(
        max_length=20,
        choices=[
            ('supportive', 'Supportive'),
            ('directive', 'Directive'),
            ('analytical', 'Analytical'),
            ('empathetic', 'Empathetic'),
        ],
        default='supportive'
    )
    
    topics_of_interest = models.JSONField(default=list, blank=True)
    
    # Privacy settings
    allow_data_analysis = models.BooleanField(default=True)
    anonymous_analytics = models.BooleanField(default=True)
    
    # UI preferences
    theme = models.CharField(
        max_length=10,
        choices=[
            ('light', 'Light'),
            ('dark', 'Dark'),
            ('system', 'System Default'),
        ],
        default='system'
    )
    
    # Reminder settings
    reminder_frequency = models.CharField(
        max_length=10,
        choices=[
            ('daily', 'Daily'),
            ('weekly', 'Weekly'),
            ('none', 'None'),
        ],
        default='none'
    )
    class Meta:
        verbose_name = "User Preference"
        verbose_name_plural = "User Preferences"
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.user.username}'s preferences"