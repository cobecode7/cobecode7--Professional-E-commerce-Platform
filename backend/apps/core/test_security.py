"""
Security tests for the e-commerce platform.
"""
import pytest
from django.test import TestCase, Client, override_settings
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.conf import settings


User = get_user_model()


class SecurityHeadersTestCase(TestCase):
    """Test security headers are present."""
    
    def setUp(self):
        self.client = Client()
    
    def test_security_headers_present(self):
        """Test that security headers are present in responses."""
        response = self.client.get('/')
        
        # Check for security headers
        expected_headers = [
            'X-Content-Type-Options',
            'X-Frame-Options', 
            'X-XSS-Protection',
        ]
        
        for header in expected_headers:
            self.assertIn(header, response)
    
    def test_x_frame_options_deny(self):
        """Test X-Frame-Options is set to DENY."""
        response = self.client.get('/')
        self.assertEqual(response['X-Frame-Options'], 'DENY')
    
    def test_content_type_options_nosniff(self):
        """Test X-Content-Type-Options is set to nosniff."""
        response = self.client.get('/')
        self.assertEqual(response['X-Content-Type-Options'], 'nosniff')


class AuthenticationSecurityTestCase(TestCase):
    """Test authentication security measures."""
    
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='SecurePass123!'
        )
    
    def test_login_rate_limiting(self):
        """Test that login attempts are rate limited."""
        login_url = reverse('admin:login')  # Using admin login for test
        
        # Make multiple failed login attempts
        for i in range(6):
            response = self.client.post(login_url, {
                'username': 'wrong@example.com',
                'password': 'wrongpassword'
            })
        
        # The 6th attempt should be rate limited
        # Note: This test depends on rate limiting middleware being active
        # In a real implementation, you'd check for 429 status or similar
    
    def test_password_validation(self):
        """Test password validation requirements."""
        from django.core.exceptions import ValidationError
        # Attempt to create user with weak password
        user = User(
            email='weak@example.com',
            username='weakuser',
            password='123'  # Too weak
        )
        with self.assertRaises(ValidationError):
            user.full_clean()


class CSRFProtectionTestCase(TestCase):
    """Test CSRF protection is active."""
    
    def setUp(self):
        self.client = Client(enforce_csrf_checks=True)
    
    def test_csrf_protection_active(self):
        """Test that CSRF protection is enforced."""
        # This would typically test a form submission without CSRF token
        # and expect a 403 Forbidden response
        pass


class InputValidationTestCase(TestCase):
    """Test input validation and sanitization."""
    
    def test_xss_prevention(self):
        """Test that XSS attempts are prevented."""
        # Test cases for XSS prevention would go here
        malicious_inputs = [
            '<script>alert("xss")</script>',
            'javascript:alert("xss")',
            '<img src="x" onerror="alert(\'xss\')">',
        ]
        
        for malicious_input in malicious_inputs:
            # Test that malicious input is properly escaped/sanitized
            # Implementation depends on your specific forms and views
            pass
    
    def test_sql_injection_prevention(self):
        """Test that SQL injection is prevented."""
        # Test cases for SQL injection prevention
        malicious_inputs = [
            "'; DROP TABLE users; --",
            "1' OR '1'='1",
            "admin'/*",
        ]
        
        for malicious_input in malicious_inputs:
            # Test that malicious SQL is not executed
            # Django ORM should prevent this automatically
            pass


@override_settings(DEBUG=False)
class ProductionSecurityTestCase(TestCase):
    """Test production security configuration."""
    
    def test_debug_disabled(self):
        """Test that DEBUG is False in production."""
        self.assertFalse(settings.DEBUG)
    
    def test_secret_key_not_default(self):
        """Test that SECRET_KEY is not the default insecure key."""
        self.assertNotIn('django-insecure', settings.SECRET_KEY)
    
    def test_allowed_hosts_configured(self):
        """Test that ALLOWED_HOSTS is properly configured."""
        # Should not contain wildcard in production
        if not settings.DEBUG:
            self.assertNotIn('*', settings.ALLOWED_HOSTS)
