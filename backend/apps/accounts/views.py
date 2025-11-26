"""Enhanced views for accounts app with JWT, 2FA, and security features."""
from typing import Any, Dict
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from rest_framework import status, generics, permissions
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError, InvalidToken
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
import qrcode
import io
import base64
from drf_spectacular.utils import extend_schema, extend_schema_view
from .models import (
    CustomUser, UserProfile, Address, LoginAttempt, 
    SecurityEvent, EmailVerificationToken
)
from .serializers import (
    CustomTokenObtainPairSerializer, UserRegistrationSerializer,
    UserProfileSerializer, AddressSerializer, PasswordChangeSerializer,
    TwoFactorSetupSerializer, TwoFactorVerifySerializer
)


class CustomTokenObtainPairView(TokenObtainPairView):
    """Enhanced JWT token obtain view with security logging."""
    serializer_class = CustomTokenObtainPairSerializer


class CustomTokenRefreshView(TokenRefreshView):
    """Enhanced JWT token refresh view with security logging."""
    
    def post(self, request, *args, **kwargs):
        """Refresh JWT token with security logging."""
        response = super().post(request, *args, **kwargs)
        
        if response.status_code == 200:
            # Log token refresh
            user = request.user if hasattr(request, 'user') else None
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            
            if user and user.is_authenticated:
                SecurityEvent.objects.create(
                    user=user,
                    event_type='login',
                    description='JWT token refreshed',
                    ip_address=ip_address,
                    user_agent=request.META.get('HTTP_USER_AGENT', '')
                )
        
        return response


@extend_schema_view(
    post=extend_schema(
        summary="Register a new user",
        description="Register a new user with enhanced security validation.",
        responses={201: "User created successfully", 400: "Validation error"}
    )
)
class UserRegistrationView(generics.CreateAPIView):
    """Enhanced user registration with security features."""
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        """Create user with email verification."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # Generate email verification token
        verification_token = EmailVerificationToken.objects.create(user=user)
        
        # Send verification email (in production, use proper email service)
        try:
            self.send_verification_email(user, verification_token)
        except Exception as e:
            # Log error but don't fail registration
            pass
        
        return Response({
            'message': 'User registered successfully. Please check your email for verification.',
            'user_id': user.id,
            'email': user.email
        }, status=status.HTTP_201_CREATED)
    
    def send_verification_email(self, user: CustomUser, token: EmailVerificationToken) -> None:
        """Send email verification email."""
        verification_url = f"http://localhost:3000/verify-email?token={token.token}"
        
        subject = 'Verify your email address'
        message = f"""
        Hi {user.first_name},
        
        Please click the link below to verify your email address:
        {verification_url}
        
        This link will expire in 24 hours.
        
        If you didn't create an account, please ignore this email.
        """
        
        try:
            send_mail(
                subject=subject,
                message=message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
                recipient_list=[user.email],
                fail_silently=True,
            )
        except Exception:
            # Email sending failed, but don't break the registration
            pass


@extend_schema(
    summary="Verify email address",
    description="Verify user's email address using the token sent via email.",
    responses={200: "Email verified successfully", 400: "Invalid or expired token"}
)
@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def verify_email(request):
    """Verify user's email address."""
    token = request.GET.get('token')
    
    if not token:
        return Response(
            {'error': 'Verification token is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        verification_token = EmailVerificationToken.objects.get(token=token)
        
        if not verification_token.is_valid:
            return Response(
                {'error': 'Token is invalid or expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Verify email and mark token as used
        user = verification_token.user
        user.is_email_verified = True
        user.save(update_fields=['is_email_verified'])
        
        verification_token.use()
        
        # Log security event
        SecurityEvent.objects.create(
            user=user,
            event_type='email_verified',
            description='User verified email address',
            ip_address=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Email verified successfully'})
        
    except EmailVerificationToken.DoesNotExist:
        return Response(
            {'error': 'Invalid verification token'},
            status=status.HTTP_400_BAD_REQUEST
        )


@extend_schema_view(
    get=extend_schema(
        summary="Get user profile",
        description="Get the current user's profile information."
    ),
    put=extend_schema(
        summary="Update user profile",
        description="Update the current user's profile information."
    ),
    patch=extend_schema(
        summary="Partially update user profile",
        description="Partially update the current user's profile information."
    )
)
class UserProfileView(generics.RetrieveUpdateAPIView):
    """User profile view with input validation."""
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        """Get or create user profile."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile
    
    def update(self, request, *args, **kwargs):
        """Update profile with security logging."""
        response = super().update(request, *args, **kwargs)
        
        if response.status_code in [200, 204]:
            # Log security event
            SecurityEvent.objects.create(
                user=request.user,
                event_type='profile_updated',
                description='User updated profile information',
                ip_address=request.META.get('REMOTE_ADDR', 'unknown'),
                user_agent=request.META.get('HTTP_USER_AGENT', '')
            )
        
        return response


class PasswordChangeView(generics.GenericAPIView):
    """Enhanced password change view with security logging."""
    serializer_class = PasswordChangeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    @extend_schema(
        summary="Change password",
        description="Change the current user's password with enhanced validation.",
        responses={200: "Password changed successfully", 400: "Validation error"}
    )
    def post(self, request, *args, **kwargs):
        """Change user password."""
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        
        return Response({
            'message': 'Password changed successfully'
        })


@extend_schema_view(
    list=extend_schema(
        summary="List user addresses",
        description="Get all addresses for the current user."
    ),
    create=extend_schema(
        summary="Create address",
        description="Create a new address for the current user."
    ),
    retrieve=extend_schema(
        summary="Get address",
        description="Get a specific address by ID."
    ),
    update=extend_schema(
        summary="Update address",
        description="Update a specific address."
    ),
    destroy=extend_schema(
        summary="Delete address",
        description="Delete a specific address."
    )
)
class AddressViewSet(ModelViewSet):
    """Address management with input validation."""
    serializer_class = AddressSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get addresses for current user only."""
        return Address.objects.filter(user=self.request.user)
    
    def perform_create(self, serializer):
        """Create address for current user."""
        serializer.save(user=self.request.user)


@extend_schema(
    summary="Logout",
    description="Logout the current user and blacklist the JWT token.",
    responses={200: "Logged out successfully"}
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    """Enhanced logout with JWT token blacklisting."""
    try:
        # Get refresh token from request
        refresh_token = request.data.get("refresh")
        
        if refresh_token:
            token = RefreshToken(refresh_token)
            token.blacklist()
        
        # Log security event
        SecurityEvent.objects.create(
            user=request.user,
            event_type='logout',
            description='User logged out',
            ip_address=request.META.get('REMOTE_ADDR', 'unknown'),
            user_agent=request.META.get('HTTP_USER_AGENT', '')
        )
        
        return Response({'message': 'Logged out successfully'})
        
    except TokenError:
        return Response(
            {'error': 'Invalid token'},
            status=status.HTTP_400_BAD_REQUEST
        )


# Legacy views for compatibility (simplified)
@extend_schema(
    summary="User registration (legacy)",
    description="Legacy user registration endpoint.",
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def register(request):
    """Legacy registration endpoint."""
    view = UserRegistrationView()
    view.request = request
    return view.create(request)


@extend_schema(
    summary="User login (legacy)",
    description="Legacy login endpoint - use JWT token endpoints instead.",
)
@api_view(['POST'])
@permission_classes([permissions.AllowAny])
def login_view(request):
    """Legacy login view - redirects to JWT."""
    return Response({
        'message': 'Please use /api/accounts/token/ for JWT authentication',
        'jwt_endpoint': '/api/accounts/token/'
    }, status=status.HTTP_200_OK)


@extend_schema(
    summary="Get current user",
    description="Get information about the currently authenticated user.",
)
@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def current_user(request):
    """Get current user information."""
    user = request.user
    return Response({
        'id': user.id,
        'email': user.email,
        'username': user.username,
        'first_name': user.first_name,
        'last_name': user.last_name,
        'is_email_verified': user.is_email_verified,
        'two_factor_enabled': user.two_factor_enabled,
        'date_joined': user.date_joined,
        'last_login': user.last_login,
    })


@extend_schema(
    summary="Send email verification",
    description="Send email verification to the current user.",
)
@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def send_email_verification(request):
    """Send email verification."""
    user = request.user
    
    if user.is_email_verified:
        return Response({'message': 'Email is already verified'})
    
    # Create verification token
    verification_token = EmailVerificationToken.objects.create(user=user)
    
    # Send verification email
    try:
        verification_url = f"http://localhost:3000/verify-email?token={verification_token.token}"
        send_mail(
            subject='Verify your email address',
            message=f'Please verify your email: {verification_url}',
            from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@example.com'),
            recipient_list=[user.email],
            fail_silently=True,
        )
        return Response({'message': 'Email verification sent'})
    except Exception:
        return Response(
            {'error': 'Failed to send verification email'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
