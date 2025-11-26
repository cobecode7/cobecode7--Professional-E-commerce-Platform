"""URL patterns for accounts app with JWT and 2FA endpoints."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView
from . import views

# Create router for ViewSets
router = DefaultRouter()
router.register(r'addresses', views.AddressViewSet, basename='address')

app_name = 'accounts'

urlpatterns = [
    # JWT Authentication endpoints
    path('token/', views.CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', views.CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    
    # User management endpoints
    path('register/', views.UserRegistrationView.as_view(), name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('current-user/', views.current_user, name='current-user'),
    
    # Profile management
    path('profile/', views.UserProfileView.as_view(), name='user-profile'),
    path('password/change/', views.PasswordChangeView.as_view(), name='password-change'),
    
    # Email verification
    path('verify-email/', views.verify_email, name='verify-email'),
    path('verify-email/send/', views.send_email_verification, name='send-email-verification'),
    
    # Include router URLs for ViewSets
    path('', include(router.urls)),
    
    # Legacy endpoints (for backward compatibility)
    path('legacy/login/', views.login_view, name='login'),
]
