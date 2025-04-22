from rest_framework import viewsets, generics, permissions, status
from rest_framework.response import Response
from rest_framework.decorators import action
from django.shortcuts import redirect 
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.views import LoginView as DjangoLoginView
from django.views.generic import TemplateView
from django.urls import reverse_lazy
from .models import CustomUser, UserPreference
from .serializers import (
    UserSerializer, UserDetailSerializer, 
    RegisterSerializer, ChangePasswordSerializer,
    UserPreferenceSerializer
)
from django.contrib.auth.views import LogoutView as DjangoLogoutView
from django.views.generic import CreateView
from .forms import CustomUserCreationForm 
from django.views.generic import UpdateView
from .forms import UserProfileForm
class WebRegisterView(CreateView):
    form_class = CustomUserCreationForm
    template_name = 'registration/register.html'
    success_url = reverse_lazy('web-login')

    def form_valid(self, form):
        # Clear previous session messages
        if self.request.session.get('registration_success'):
            del self.request.session['registration_success']
            
        response = super().form_valid(form)
        self.request.session['registration_success'] = True
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['registration_success'] = self.request.session.get('registration_success', False)
        return context

class WebLogoutView(DjangoLogoutView):
    next_page = reverse_lazy('home')

class UserViewSet(viewsets.ModelViewSet):
    """API endpoint for user management"""
    queryset = CustomUser.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]  # Only admins can manage users

    def get_serializer_class(self):
        if self.action in ['retrieve', 'update', 'partial_update']:
            return UserDetailSerializer
        return super().get_serializer_class()

    @action(detail=False, methods=['get'], permission_classes=[permissions.IsAuthenticated])
    def me(self, request):
        """Get current user details"""
        serializer = UserDetailSerializer(request.user, context={'request': request})
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def logout(self, request):
        """API logout endpoint"""
        logout(request)
        return Response({"detail": "Successfully logged out."}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change_password(self, request):
        """Change password endpoint"""
        serializer = ChangePasswordSerializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            request.user.set_password(serializer.validated_data['new_password'])
            request.user.save()
            return Response({"detail": "Password updated successfully"})
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RegisterView(generics.CreateAPIView):
    """User registration endpoint"""
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        headers = self.get_success_headers(serializer.data)
        return Response(
            UserDetailSerializer(user, context=self.get_serializer_context()).data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

class LoginView(generics.GenericAPIView):
    """API login endpoint"""
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.AllowAny]

    def post(self, request, *args, **kwargs):
        username = request.data.get('username')
        password = request.data.get('password')

        user = authenticate(request, username=username, password=password)
        if not user:
            return Response(
                {"detail": "Invalid credentials"},
                status=status.HTTP_401_UNAUTHORIZED
            )

        login(request, user)
        serializer = self.get_serializer(user)
        return Response(serializer.data)

class WebLoginView(DjangoLoginView):
    """Web interface login view"""
    template_name = 'registration/login.html'
    redirect_authenticated_user = True
    success_url = reverse_lazy('home')

class UserPreferenceView(generics.RetrieveUpdateAPIView):
    """User preferences endpoint"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        obj, created = UserPreference.objects.get_or_create(user=self.request.user)
        return obj

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

# Web interface views
class ProfileView(TemplateView):
    """User profile web view"""
    template_name = 'users/profile.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        context.update({
            'user': user,
            'preferences': user.preferences,
            'emergency_contact': {
                'name': user.emergency_contact_name,
                'phone': user.emergency_contact_phone
            }
        })
        return context
class ProfileUpdateView(UpdateView):
    form_class = UserProfileForm
    template_name = 'users/profile.html'
    success_url = reverse_lazy('user-profile')

    def get_object(self):
        return self.request.user

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['emergency_contact'] = {
            'name': self.object.emergency_contact_name,
            'phone': self.object.emergency_contact_phone
        }
        return context
        
class WebPreferencesView(TemplateView):
    template_name = 'users/preferences.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        preferences, created = UserPreference.objects.get_or_create(user=user)
        context['preferences'] = preferences
        return context
    
    def post(self, request, *args, **kwargs):
        preferences = request.user.preferences
        # Add your preference update logic here
        return redirect('user-preferences')
    
class UserList(generics.ListCreateAPIView):
    """API endpoint for listing or creating users"""
    queryset = CustomUser.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAdminUser]

class UserDetail(generics.RetrieveUpdateDestroyAPIView):
    """API endpoint for individual user management"""
    queryset = CustomUser.objects.all()
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAdminUser]

class UserPreferenceAPI(generics.RetrieveUpdateAPIView):
    """API endpoint for user preferences"""
    serializer_class = UserPreferenceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user.preferences    