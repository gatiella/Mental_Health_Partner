from django.contrib import admin
from django.urls import path, include
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from django.views.generic import TemplateView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    # Admin
    path('admin/', admin.site.urls),
    
    # Web Interface
    path('', TemplateView.as_view(template_name='home.html'), name='home'),
    path('about/', TemplateView.as_view(template_name='about.html'), name='about'),
    path('privacy/', TemplateView.as_view(template_name='privacy.html'), name='privacy'),
    path('terms/', TemplateView.as_view(template_name='terms.html'), name='terms'),
    path('contact/', TemplateView.as_view(template_name='contact.html'), name='contact'),
    
    # Authentication
    path('accounts/', include('django.contrib.auth.urls')),
    
    # Apps
    path('conversations/', include('conversation.urls_web')),
    path('users/', include('users.urls')),
    
    # API Endpoints
    path('api/auth/', include('rest_framework.urls', namespace='rest_framework')),
    path('api/conversations/', include('conversation.urls')),
    path('api/users/', include('users.urls')),  # Changed to include users.urls
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Add API root view at the end to avoid circular imports
@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'conversations': reverse('conversation-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'prompts': reverse('prompt-list', request=request, format=format),
    })

urlpatterns += [
    path('api/', api_root, name='api-root'),
]