from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = CustomUser
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user
    
class UserProfileForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = [
            'profile_picture',
            'username',
            'email',
            'date_of_birth',
            'emergency_contact_name',
            'emergency_contact_phone',
            'mental_health_history'
        ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'mental_health_history': forms.Textarea(attrs={'rows': 4}),
        }
        help_texts = {
            'username': None,  # Remove default username help text
        }    