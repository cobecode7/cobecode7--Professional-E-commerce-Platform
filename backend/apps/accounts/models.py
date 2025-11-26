"""User models for the ecommerce platform."""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import RegexValidator
from phonenumber_field.modelfields import PhoneNumberField
from django.utils import timezone
from datetime import timedelta
import secrets


class CustomUser(AbstractUser):
    """Custom user model with email as the primary identifier and enhanced security."""
    
    email = models.EmailField(
        unique=True,
        verbose_name="Email Address"
    )
    phone_number = PhoneNumberField(
        blank=True,
        null=True,
        help_text="Phone number for SMS notifications and 2FA"
    )
    is_email_verified = models.BooleanField(default=False)
    is_phone_verified = models.BooleanField(default=False)
    date_of_birth = models.DateField(blank=True, null=True)
    
    # Security and privacy fields
    two_factor_enabled = models.BooleanField(
        default=False,
        help_text="Whether user has enabled 2FA"
    )
    last_password_change = models.DateTimeField(
        default=timezone.now,
        help_text="When user last changed password"
    )
    password_reset_required = models.BooleanField(
        default=False,
        help_text="Force password reset on next login"
    )
    failed_login_attempts = models.PositiveIntegerField(
        default=0,
        help_text="Number of consecutive failed login attempts"
    )
    account_locked_until = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Account locked until this time"
    )
    last_login_ip = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="IP address of last login"
    )
    
    # Privacy preferences
    marketing_emails = models.BooleanField(
        default=False,
        help_text="Consent to receive marketing emails"
    )
    data_processing_consent = models.BooleanField(
        default=False,
        help_text="GDPR data processing consent"
    )
    consent_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When user gave consent"
    )
    
    # Use email instead of username for authentication
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']
    
    class Meta:
        verbose_name = "User"
        verbose_name_plural = "Users"
        app_label = "accounts"
        
    def __str__(self) -> str:
        """Return string representation of user."""
        return f"{self.email} ({self.get_full_name() or self.username})"
    
    @property
    def full_name(self) -> str:
        """Return user's full name."""
        return self.get_full_name() or self.username
    
    @property
    def is_account_locked(self) -> bool:
        """Check if account is currently locked."""
        if self.account_locked_until:
            return timezone.now() < self.account_locked_until
        return False
    
    def lock_account(self, duration_minutes: int = 30) -> None:
        """Lock account for specified duration."""
        self.account_locked_until = timezone.now() + timedelta(minutes=duration_minutes)
        self.save(update_fields=['account_locked_until'])
    
    def unlock_account(self) -> None:
        """Unlock account and reset failed attempts."""
        self.account_locked_until = None
        self.failed_login_attempts = 0
        self.save(update_fields=['account_locked_until', 'failed_login_attempts'])
    
    def increment_failed_login(self) -> None:
        """Increment failed login attempts and lock if necessary."""
        self.failed_login_attempts += 1
        if self.failed_login_attempts >= 5:  # Lock after 5 failed attempts
            self.lock_account(duration_minutes=30)
        self.save(update_fields=['failed_login_attempts'])
    
    def reset_failed_login_attempts(self) -> None:
        """Reset failed login attempts on successful login."""
        if self.failed_login_attempts > 0:
            self.failed_login_attempts = 0
            self.save(update_fields=['failed_login_attempts'])
    
    def update_last_login_ip(self, ip_address: str) -> None:
        """Update last login IP address."""
        self.last_login_ip = ip_address
        self.save(update_fields=['last_login_ip'])
    
    def is_password_expired(self, max_age_days: int = 90) -> bool:
        """Check if password needs to be changed."""
        if self.password_reset_required:
            return True
        if self.last_password_change:
            return timezone.now() > self.last_password_change + timedelta(days=max_age_days)
        return False


class UserProfile(models.Model):
    """Extended user profile information."""
    
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='profile'
    )
    bio = models.TextField(max_length=500, blank=True)
    avatar = models.ImageField(
        upload_to='avatars/%Y/%m/%d/',
        blank=True,
        null=True,
        help_text="Profile picture (max 2MB)"
    )
    website = models.URLField(blank=True)
    location = models.CharField(max_length=100, blank=True)
    
    # Notification preferences
    email_notifications = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=False)
    push_notifications = models.BooleanField(default=True)
    
    # Security preferences
    login_notifications = models.BooleanField(
        default=True,
        help_text="Email notifications for new logins"
    )
    security_alerts = models.BooleanField(
        default=True,
        help_text="Email alerts for security events"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"
        
    def __str__(self) -> str:
        """Return string representation of profile."""
        return f"Profile of {self.user.email}"


class Address(models.Model):
    """User addresses for shipping and billing."""
    
    ADDRESS_TYPES = [
        ('shipping', 'Shipping Address'),
        ('billing', 'Billing Address'),
        ('both', 'Shipping & Billing'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='addresses'
    )
    type = models.CharField(max_length=10, choices=ADDRESS_TYPES)
    
    # Address fields
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True)
    address_line_1 = models.CharField(max_length=255)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postal_code = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default='United States')
    
    # Metadata
    is_default = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Address"
        verbose_name_plural = "Addresses"
        unique_together = [['user', 'type', 'is_default']]  # Only one default address per type per user
        
    def __str__(self) -> str:
        """Return string representation of address."""
        return f"{self.first_name} {self.last_name} - {self.city}, {self.state}"
    
    @property
    def full_address(self) -> str:
        """Return formatted full address."""
        lines = [
            f"{self.first_name} {self.last_name}",
            self.company if self.company else None,
            self.address_line_1,
            self.address_line_2 if self.address_line_2 else None,
            f"{self.city}, {self.state} {self.postal_code}",
            self.country
        ]
        return '\n'.join(line for line in lines if line)


class EmailVerificationToken(models.Model):
    """Email verification tokens for user registration."""
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='email_verification_tokens'
    )
    token = models.CharField(max_length=128, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Email Verification Token"
        verbose_name_plural = "Email Verification Tokens"
    
    def save(self, *args, **kwargs):
        if not self.token:
            self.token = secrets.token_urlsafe(64)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired."""
        return timezone.now() > self.expires_at
    
    @property
    def is_valid(self) -> bool:
        """Check if token is valid (not expired and not used)."""
        return not self.is_expired and not self.is_used
    
    def use(self) -> bool:
        """Mark token as used if valid."""
        if self.is_valid:
            self.is_used = True
            self.save(update_fields=['is_used'])
            return True
        return False


class LoginAttempt(models.Model):
    """Track login attempts for security monitoring."""
    
    SUCCESS = 'success'
    FAILED = 'failed'
    BLOCKED = 'blocked'
    
    ATTEMPT_CHOICES = [
        (SUCCESS, 'Success'),
        (FAILED, 'Failed'),
        (BLOCKED, 'Blocked'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='login_attempts',
        null=True,
        blank=True
    )
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    attempt_type = models.CharField(max_length=10, choices=ATTEMPT_CHOICES)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional context
    failure_reason = models.CharField(max_length=100, blank=True)
    two_factor_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = "Login Attempt"
        verbose_name_plural = "Login Attempts"
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.email} - {self.attempt_type} at {self.timestamp}"


class SecurityEvent(models.Model):
    """Security events for audit and monitoring."""
    
    EVENT_TYPES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('password_change', 'Password Change'),
        ('password_reset', 'Password Reset'),
        ('2fa_enabled', '2FA Enabled'),
        ('2fa_disabled', '2FA Disabled'),
        ('account_locked', 'Account Locked'),
        ('account_unlocked', 'Account Unlocked'),
        ('email_verified', 'Email Verified'),
        ('profile_updated', 'Profile Updated'),
        ('suspicious_activity', 'Suspicious Activity'),
    ]
    
    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='security_events'
    )
    event_type = models.CharField(max_length=20, choices=EVENT_TYPES)
    description = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Additional metadata
    metadata = models.JSONField(default=dict, blank=True)
    
    class Meta:
        verbose_name = "Security Event"
        verbose_name_plural = "Security Events"
        ordering = ['-timestamp']
    
    def __str__(self) -> str:
        return f"{self.user.email} - {self.get_event_type_display()} at {self.timestamp}"
