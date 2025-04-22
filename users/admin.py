from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser, UserPreference

class UserPreferenceInline(admin.StackedInline):
    model = UserPreference
    can_delete = False
    verbose_name_plural = 'Preferences'

class CustomUserAdmin(UserAdmin):
    inlines = (UserPreferenceInline,)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')
    fieldsets = UserAdmin.fieldsets + (
        ('Personal Info', {'fields': ('date_of_birth', 'profile_picture', 'bio')}),
        ('Mental Health', {'fields': ('mental_health_history', 'emergency_contact_name', 'emergency_contact_phone')}),
        ('Preferences', {'fields': ('notification_preferences', 'therapy_preferences')}),
    )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UserPreference)