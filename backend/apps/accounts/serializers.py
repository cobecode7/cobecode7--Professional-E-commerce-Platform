"""Serializers for the accounts app with enhanced security and validation."""
import re
from typing import Dict, Any
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django_otp import user_has_device
from django_otp.plugins.otp_totp.models import TOTPDevice
import bleach
from phonenumber_field.serializerfields import PhoneNumberField
from .models import (
    CustomUser, UserProfile, Address, LoginAttempt, 
    SecurityEvent, EmailVerificationToken
)


class InputSanitizationMixin:
    """Mixin to sanitize text inputs and prevent XSS."""
    
    ALLOWED_TAGS = ['b', 'i', 'em', 'strong', 'p', 'br']
    ALLOWED_ATTRIBUTES = {}
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text input to prevent XSS."""
        if not text:
            return text
        return bleach.clean(
            text, 
            tags=self.ALLOWED_TAGS, 
            attributes=self.ALLOWED_ATTRIBUTES,
            strip=True
        )
    
    def validate_no_scripts(self, value: str) -> str:
        """Ensure no script tags or javascript in input."""
        if not value:
            return value
        
        # Check for script tags or javascript protocols
        dangerous_patterns = [
            r'<script.*?>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'<iframe.*?>.*?</iframe>',
        ]
        
        for pattern in dangerous_patterns:
            if re.search(pattern, value, re.IGNORECASE):
                raise serializers.ValidationError(
                    "Input contains potentially dangerous content."
                )
        
        return self.sanitize_text(value)


class PasswordValidationMixin:
    """Mixin for advanced password validation."""
    
    def validate_password_strength(self, password: str) -> str:
        """Validate password strength beyond Django's default."""
        if len(password) < 12:
            raise serializers.ValidationError(
                "Password must be at least 12 characters long."
            )
        
        # Check for common patterns
        if password.lower() in ['password', '12345678', 'qwerty']:
            raise serializers.ValidationError(
                "Password is too common."
            )
        
        # Check for character variety
        has_upper = bool(re.search(r'[A-Z]', password))
        has_lower = bool(re.search(r'[a-z]', password))
        has_digit = bool(re.search(r'\d', password))
        has_special = bool(re.search(r'[!@#$%^&*(),.?":{}|<>]', password))
        
        if not (has_upper and has_lower and has_digit and has_special):
            raise serializers.ValidationError(
                "Password must contain uppercase, lowercase, digit, and special characters."
            )
        
        # Use Django's built-in validators
        try:
            validate_password(password)
        except ValidationError as e:
            raise serializers.ValidationError(e.messages)
        
        return password


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Enhanced JWT token serializer with security features."""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.request = self.context.get('request')
    
    def validate(self, attrs):
        """Enhanced validation with security logging."""
        email = attrs.get('email') or attrs.get('username')
        password = attrs.get('password')
        
        if not email or not password:
            raise serializers.ValidationError(
                "Email and password are required."
            )
        
        # Get IP address for logging
        ip_address = self.get_client_ip()
        user_agent = self.request.META.get('HTTP_USER_AGENT', '') if self.request else ''
        
        try:
            # Try to get user first for security logging
            try:
                user = CustomUser.objects.get(email=email)
            except CustomUser.DoesNotExist:
                user = None
            
            # Check if account is locked
            if user and user.is_account_locked:
                LoginAttempt.objects.create(
                    user=user,
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    attempt_type=LoginAttempt.BLOCKED,
                    failure_reason='Account locked'
                )
                raise serializers.ValidationError(
                    "Account is temporarily locked. Please try again later."
                )
            
            # Authenticate user
            user = authenticate(
                request=self.request,
                username=email,
                password=password
            )
            
            if not user:
                # Log failed attempt
                LoginAttempt.objects.create(
                    user=user,
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    attempt_type=LoginAttempt.FAILED,
                    failure_reason='Invalid credentials'
                )
                
                # Increment failed attempts for existing user
                if user:
                    user.increment_failed_login()
                
                raise serializers.ValidationError(
                    "Invalid email or password."
                )
            
            if not user.is_active:
                LoginAttempt.objects.create(
                    user=user,
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    attempt_type=LoginAttempt.BLOCKED,
                    failure_reason='Account inactive'
                )
                raise serializers.ValidationError(
                    "Account is inactive."
                )
            
            # Check for 2FA requirement
            if user.two_factor_enabled and user_has_device(user):
                # This should be handled by a separate 2FA endpoint
                # For now, we'll include a flag in the response
                pass
            
            # Successful login
            user.reset_failed_login_attempts()
            user.update_last_login_ip(ip_address)
            
            # Log successful login
            LoginAttempt.objects.create(
                user=user,
                email=email,
                ip_address=ip_address,
                user_agent=user_agent,
                attempt_type=LoginAttempt.SUCCESS,
                two_factor_used=user.two_factor_enabled
            )
            
            # Create security event
            SecurityEvent.objects.create(
                user=user,
                event_type='login',
                description='User logged in successfully',
                ip_address=ip_address,
                user_agent=user_agent,
                metadata={'two_factor_used': user.two_factor_enabled}
            )
            
            # Generate tokens
            refresh = RefreshToken.for_user(user)
            
            return {
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'name': user.get_full_name(),
                    'is_verified': user.is_email_verified,
                    'two_factor_enabled': user.two_factor_enabled,
                    'requires_2fa': user.two_factor_enabled and user_has_device(user),
                }
            }
            
        except Exception as e:
            # Log any unexpected errors
            if user:
                LoginAttempt.objects.create(
                    user=user,
                    email=email,
                    ip_address=ip_address,
                    user_agent=user_agent,
                    attempt_type=LoginAttempt.FAILED,
                    failure_reason=f'Error: {str(e)}'
                )
            raise
    
    def get_client_ip(self) -> str:
        """Get client IP address from request."""
        if not self.request:
            return 'unknown'
        
        x_forwarded_for = self.request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return self.request.META.get('REMOTE_ADDR', 'unknown')


class UserRegistrationSerializer(serializers.ModelSerializer, InputSanitizationMixin, PasswordValidationMixin):
    """Enhanced user registration serializer with comprehensive validation."""
    
    password = serializers.CharField(write_only=True)
    password_confirm = serializers.CharField(write_only=True)
    phone_number = PhoneNumberField(required=False, allow_blank=True)
    data_processing_consent = serializers.BooleanField(required=True)
    marketing_emails = serializers.BooleanField(required=False, default=False)
    
    class Meta:
        model = CustomUser
        fields = [
            'username', 'email', 'first_name', 'last_name', 
            'phone_number', 'password', 'password_confirm',
            'data_processing_consent', 'marketing_emails'
        ]
        extra_kwargs = {
            'username': {'required': True},
            'email': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
        }
    
    def validate_email(self, value: str) -> str:
        """Validate and sanitize email."""
        if not value:
            raise serializers.ValidationError("Email is required.")
        
        # Basic email format validation
        email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        if not re.match(email_regex, value):
            raise serializers.ValidationError("Enter a valid email address.")
        
        # Check for existing email
        if CustomUser.objects.filter(email=value.lower()).exists():
            raise serializers.ValidationError(
                "A user with this email already exists."
            )
        
        return value.lower()
    
    def validate_username(self, value: str) -> str:
        """Validate and sanitize username."""
        value = self.validate_no_scripts(value)
        
        # Username format validation
        if len(value) < 3:
            raise serializers.ValidationError(
                "Username must be at least 3 characters long."
            )
        
        if not re.match(r'^[a-zA-Z0-9_.-]+$', value):
            raise serializers.ValidationError(
                "Username can only contain letters, numbers, and ._- characters."
            )
        
        # Check for existing username
        if CustomUser.objects.filter(username=value).exists():
            raise serializers.ValidationError(
                "A user with this username already exists."
            )
        
        return value
    
    def validate_first_name(self, value: str) -> str:
        """Validate and sanitize first name."""
        return self.validate_no_scripts(value)
    
    def validate_last_name(self, value: str) -> str:
        """Validate and sanitize last name."""
        return self.validate_no_scripts(value)
    
    def validate_data_processing_consent(self, value: bool) -> bool:
        """Validate GDPR consent."""
        if not value:
            raise serializers.ValidationError(
                "You must consent to data processing to create an account."
            )
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-field validation."""
        password = attrs.get('password')
        password_confirm = attrs.get('password_confirm')
        
        if password != password_confirm:
            raise serializers.ValidationError({
                'password_confirm': "Passwords do not match."
            })
        
        # Validate password strength
        self.validate_password_strength(password)
        
        # Remove password_confirm as it's not needed for user creation
        attrs.pop('password_confirm', None)
        
        return attrs
    
    def create(self, validated_data: Dict[str, Any]) -> CustomUser:
        """Create user with enhanced security."""
        # Extract non-user fields
        marketing_emails = validated_data.pop('marketing_emails', False)
        
        # Create user
        user = CustomUser.objects.create_user(**validated_data)
        
        # Set additional fields
        user.marketing_emails = marketing_emails
        user.data_processing_consent = True
        user.consent_date = timezone.now()
        user.save(update_fields=['marketing_emails', 'data_processing_consent', 'consent_date'])
        
        # Create profile
        UserProfile.objects.create(
            user=user,
            email_notifications=True,
            login_notifications=True,
            security_alerts=True
        )
        
        # Create security event
        request = self.context.get('request')
        ip_address = 'unknown'
        user_agent = ''
        
        if request:
            ip_address = request.META.get('REMOTE_ADDR', 'unknown')
            user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        SecurityEvent.objects.create(
            user=user,
            event_type='login',  # Registration is a type of login event
            description='User account created',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return user


class UserProfileSerializer(serializers.ModelSerializer, InputSanitizationMixin):
    """Serializer for user profile with input sanitization."""
    
    class Meta:
        model = UserProfile
        fields = [
            'bio', 'avatar', 'website', 'location',
            'email_notifications', 'sms_notifications', 'push_notifications',
            'login_notifications', 'security_alerts'
        ]
    
    def validate_bio(self, value: str) -> str:
        """Sanitize bio content."""
        return self.sanitize_text(value)
    
    def validate_location(self, value: str) -> str:
        """Sanitize location."""
        return self.validate_no_scripts(value)
    
    def validate_website(self, value: str) -> str:
        """Validate website URL."""
        if value and not value.startswith(('http://', 'https://')):
            value = f'https://{value}'
        return value


class AddressSerializer(serializers.ModelSerializer, InputSanitizationMixin):
    """Serializer for addresses with input validation."""
    
    class Meta:
        model = Address
        fields = [
            'id', 'type', 'first_name', 'last_name', 'company',
            'address_line_1', 'address_line_2', 'city', 'state',
            'postal_code', 'country', 'is_default'
        ]
    
    def validate_first_name(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_last_name(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_company(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_address_line_1(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_address_line_2(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_city(self, value: str) -> str:
        return self.validate_no_scripts(value)
    
    def validate_state(self, value: str) -> str:
        return self.validate_no_scripts(value)


class PasswordChangeSerializer(serializers.Serializer, PasswordValidationMixin):
    """Serializer for password change with enhanced validation."""
    
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)
    new_password_confirm = serializers.CharField(required=True)
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Validate password change."""
        user = self.context['request'].user
        current_password = attrs['current_password']
        new_password = attrs['new_password']
        new_password_confirm = attrs['new_password_confirm']
        
        # Verify current password
        if not user.check_password(current_password):
            raise serializers.ValidationError({
                'current_password': 'Current password is incorrect.'
            })
        
        # Check if new password is different
        if current_password == new_password:
            raise serializers.ValidationError({
                'new_password': 'New password must be different from current password.'
            })
        
        # Confirm new passwords match
        if new_password != new_password_confirm:
            raise serializers.ValidationError({
                'new_password_confirm': 'New passwords do not match.'
            })
        
        # Validate new password strength
        self.validate_password_strength(new_password)
        
        return attrs
    
    def save(self) -> None:
        """Change user password and log the event."""
        user = self.context['request'].user
        new_password = self.validated_data['new_password']
        
        user.set_password(new_password)
        user.last_password_change = timezone.now()
        user.save(update_fields=['password', 'last_password_change'])
        
        # Log security event
        request = self.context['request']
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        SecurityEvent.objects.create(
            user=user,
            event_type='password_change',
            description='User changed password',
            ip_address=ip_address,
            user_agent=user_agent
        )


class TwoFactorSetupSerializer(serializers.Serializer):
    """Serializer for 2FA setup."""
    
    def create_totp_device(self, user: CustomUser) -> Dict[str, Any]:
        """Create TOTP device for user."""
        device = TOTPDevice.objects.create(
            user=user,
            name='default',
            confirmed=False
        )
        
        # Generate QR code data
        qr_url = device.config_url
        
        return {
            'device_id': device.id,
            'qr_url': qr_url,
            'secret_key': device.bin_key.hex(),
            'backup_tokens': []  # TODO: Generate backup tokens
        }


class TwoFactorVerifySerializer(serializers.Serializer):
    """Serializer for 2FA verification."""
    
    device_id = serializers.IntegerField()
    token = serializers.CharField(max_length=6, min_length=6)
    
    def validate_token(self, value: str) -> str:
        """Validate TOTP token format."""
        if not value.isdigit():
            raise serializers.ValidationError("Token must be 6 digits.")
        return value
    
    def validate(self, attrs: Dict[str, Any]) -> Dict[str, Any]:
        """Verify TOTP token."""
        user = self.context['request'].user
        device_id = attrs['device_id']
        token = attrs['token']
        
        try:
            device = TOTPDevice.objects.get(id=device_id, user=user)
        except TOTPDevice.DoesNotExist:
            raise serializers.ValidationError("Invalid device.")
        
        if not device.verify_token(token):
            raise serializers.ValidationError("Invalid token.")
        
        # Confirm device and enable 2FA
        device.confirmed = True
        device.save()
        
        user.two_factor_enabled = True
        user.save(update_fields=['two_factor_enabled'])
        
        # Log security event
        request = self.context['request']
        ip_address = request.META.get('REMOTE_ADDR', 'unknown')
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        
        SecurityEvent.objects.create(
            user=user,
            event_type='2fa_enabled',
            description='User enabled 2FA',
            ip_address=ip_address,
            user_agent=user_agent
        )
        
        return attrs
