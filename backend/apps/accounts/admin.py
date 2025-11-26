"""Admin configuration for accounts app with enhanced security features."""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.utils.html import format_html
from django.utils.translation import gettext_lazy as _
from .models import (
    CustomUser, UserProfile, Address, LoginAttempt,
    SecurityEvent, EmailVerificationToken
)


class CustomUserAdmin(UserAdmin):
    """Enhanced admin for CustomUser with security fields."""
    
    # Display fields
    list_display = (
        'email', 'username', 'first_name', 'last_name', 
        'is_email_verified', 'two_factor_enabled', 'is_active', 
        'is_staff', 'date_joined', 'last_login'
    )
    list_filter = (
        'is_active', 'is_staff', 'is_superuser', 
        'is_email_verified', 'two_factor_enabled',
        'marketing_emails', 'data_processing_consent',
        'date_joined', 'last_login'
    )
    search_fields = ('email', 'username', 'first_name', 'last_name')
    ordering = ('-date_joined',)
    
    # Form fields
    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth')
        }),
        (_('Verification'), {
            'fields': ('is_email_verified', 'is_phone_verified')
        }),
        (_('Security'), {
            'fields': (
                'two_factor_enabled', 'last_password_change', 
                'password_reset_required', 'failed_login_attempts',
                'account_locked_until', 'last_login_ip'
            )
        }),
        (_('Privacy'), {
            'fields': (
                'marketing_emails', 'data_processing_consent', 
                'consent_date'
            )
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')
        }),
        (_('Important dates'), {
            'fields': ('last_login', 'date_joined')
        }),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': (
                'email', 'username', 'first_name', 'last_name',
                'password1', 'password2', 'is_staff', 'is_active'
            )
        }),
    )
    
    readonly_fields = (
        'date_joined', 'last_login', 'last_password_change',
        'failed_login_attempts', 'last_login_ip', 'consent_date'
    )


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """Admin for UserProfile."""
    
    list_display = (
        'user', 'location', 'email_notifications', 
        'login_notifications', 'security_alerts', 'created_at'
    )
    list_filter = (
        'email_notifications', 'sms_notifications', 'push_notifications',
        'login_notifications', 'security_alerts', 'created_at'
    )
    search_fields = ('user__email', 'user__username', 'location')
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    """Admin for Address."""
    
    list_display = (
        'user', 'type', 'first_name', 'last_name', 
        'city', 'state', 'is_default', 'created_at'
    )
    list_filter = ('type', 'is_default', 'country', 'created_at')
    search_fields = (
        'user__email', 'first_name', 'last_name', 
        'city', 'state', 'postal_code'
    )
    readonly_fields = ('created_at', 'updated_at')


@admin.register(LoginAttempt)
class LoginAttemptAdmin(admin.ModelAdmin):
    """Admin for LoginAttempt with security monitoring."""
    
    list_display = (
        'email', 'ip_address', 'attempt_type', 
        'two_factor_used', 'timestamp', 'failure_reason'
    )
    list_filter = (
        'attempt_type', 'two_factor_used', 'timestamp'
    )
    search_fields = ('email', 'ip_address', 'failure_reason')
    readonly_fields = ('timestamp',)
    date_hierarchy = 'timestamp'


@admin.register(SecurityEvent)
class SecurityEventAdmin(admin.ModelAdmin):
    """Admin for SecurityEvent with monitoring capabilities."""
    
    list_display = (
        'user', 'event_type', 'description', 
        'ip_address', 'timestamp'
    )
    list_filter = ('event_type', 'timestamp')
    search_fields = ('user__email', 'description', 'ip_address')
    readonly_fields = ('timestamp', 'metadata')
    date_hierarchy = 'timestamp'


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    """Admin for EmailVerificationToken."""
    
    list_display = (
        'user', 'is_valid_status', 'created_at', 'expires_at', 'is_used'
    )
    list_filter = ('is_used', 'created_at', 'expires_at')
    search_fields = ('user__email', 'token')
    readonly_fields = ('token', 'created_at', 'expires_at')
    
    def is_valid_status(self, obj):
        """Display token validity status."""
        if obj.is_valid:
            return format_html('<span style="color: green;">✓ Valid</span>')
        elif obj.is_used:
            return format_html('<span style="color: blue;">✓ Used</span>')
        else:
            return format_html('<span style="color: red;">✗ Expired</span>')
    is_valid_status.short_description = 'Status'


# Register the custom user admin
admin.site.register(CustomUser, CustomUserAdmin)

# Configure admin site
admin.site.site_header = 'E-commerce Security Administration'
admin.site.site_title = 'E-commerce Admin'
admin.site.index_title = 'Security & User Management'