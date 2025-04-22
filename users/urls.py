from django.urls import path, include
from . import views
from django.views.generic import RedirectView

# Web interface URLs
urlpatterns = [
    path('web-login/', views.WebLoginView.as_view(), name='web-login'),
    path('login/', RedirectView.as_view(pattern_name='web-login', permanent=True)),
    path('logout/', views.WebLogoutView.as_view(), name='web-logout'),
    path('register/', views.WebRegisterView.as_view(), name='register'),
    path('profile/', views.ProfileUpdateView.as_view(), name='user-profile'),
    path('preferences/', views.WebPreferencesView.as_view(), name='user-preferences'),
    # Other web routes...
]

# API URLs
api_patterns = [
    path('login/', views.LoginView.as_view(), name='api-login'),
    path('logout/', views.UserViewSet.as_view({'post': 'logout'}), name='api-logout'),
    path('register/', views.RegisterView.as_view(), name='api-register'),
    path('me/', views.UserViewSet.as_view({'get': 'me'}), name='api-current-user'),
    path('preferences/', views.UserPreferenceAPI.as_view(), name='api-user-preferences'),
    path('', views.UserList.as_view(), name='user-list'),
    path('<int:pk>/', views.UserDetail.as_view(), name='user-detail'),
    # Other API routes...
]

# Include API routes under the api/ namespace
urlpatterns += [
    path('api/', include((api_patterns, 'api'))),
    #path('api/', include((api_patterns, 'users_api'))),
]