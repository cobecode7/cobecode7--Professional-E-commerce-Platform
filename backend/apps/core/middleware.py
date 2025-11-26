"""
Custom security middleware for enhanced protection.
"""
import logging
import time
from typing import Callable
from django.http import HttpRequest, HttpResponse
from django.core.cache import cache
from django.conf import settings
from django.utils.deprecation import MiddlewareMixin
import ipaddress

# Setup security logger
security_logger = logging.getLogger('security')


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    """
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Add security headers to response."""
        security_headers = getattr(settings, 'SECURITY_HEADERS', {})
        
        # Default security headers
        default_headers = {
            'X-Content-Type-Options': 'nosniff',
            'X-Frame-Options': getattr(settings, 'X_FRAME_OPTIONS', 'SAMEORIGIN'),
            'X-XSS-Protection': '1; mode=block',
            'Referrer-Policy': 'strict-origin-when-cross-origin',
            'Permissions-Policy': 'geolocation=(), microphone=(), camera=()',
        }
        
        # Merge with custom headers
        headers = {**default_headers, **security_headers}
        
        # Add Content Security Policy if not an API endpoint
        if not request.path.startswith('/api/'):
            csp = getattr(settings, 'SECURE_CONTENT_SECURITY_POLICY', None)
            if csp:
                headers['Content-Security-Policy'] = csp
        
        # Add all headers to response
        for header, value in headers.items():
            response[header] = value
        
        return response


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log security-relevant requests.
    """
    
    # Paths that should be logged for security monitoring
    SECURITY_PATHS = [
        '/admin/',
        '/api/auth/',
        '/api/accounts/login/',
        '/api/accounts/register/',
        '/api/accounts/password-reset/',
    ]
    
    # Suspicious patterns
    SUSPICIOUS_PATTERNS = [
        'union select',
        'drop table',
        '<script',
        'javascript:',
        '../../../',
        '..\\..\\',
    ]
    
    def process_request(self, request: HttpRequest) -> None:
        """Log security-relevant requests."""
        # Store request start time
        request.start_time = time.time()
        
        # Get client IP
        ip = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        path = request.path
        method = request.method
        
        # Log admin and authentication attempts
        if any(path.startswith(security_path) for security_path in self.SECURITY_PATHS):
            security_logger.warning(
                f"Security path access: {method} {path} from {ip} - {user_agent}"
            )
        
        # Check for suspicious patterns in query parameters
        query_string = request.META.get('QUERY_STRING', '').lower()
        if any(pattern in query_string for pattern in self.SUSPICIOUS_PATTERNS):
            security_logger.error(
                f"Suspicious query detected: {method} {path}?{query_string} from {ip} - {user_agent}"
            )
        
        # Check for suspicious user agents
        if self.is_suspicious_user_agent(user_agent):
            security_logger.warning(
                f"Suspicious user agent: {user_agent} from {ip} accessing {path}"
            )
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Log response details for security monitoring."""
        # Calculate request duration
        if hasattr(request, 'start_time'):
            duration = time.time() - request.start_time
            
            # Log slow requests (potential DoS attempts)
            if duration > 5.0:  # 5 seconds
                ip = self.get_client_ip(request)
                security_logger.warning(
                    f"Slow request detected: {request.method} {request.path} "
                    f"took {duration:.2f}s from {ip}"
                )
        
        # Log failed authentication attempts
        if response.status_code in [401, 403] and request.path.startswith('/api/'):
            ip = self.get_client_ip(request)
            security_logger.warning(
                f"Authentication failed: {request.method} {request.path} "
                f"returned {response.status_code} from {ip}"
            )
        
        return response
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """Get the real client IP address."""
        # Check for IP in various headers (for reverse proxies)
        headers_to_check = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CF_CONNECTING_IP',  # Cloudflare
            'REMOTE_ADDR',
        ]
        
        for header in headers_to_check:
            ip = request.META.get(header)
            if ip:
                # Handle comma-separated IPs (X-Forwarded-For)
                ip = ip.split(',')[0].strip()
                try:
                    # Validate IP address
                    ipaddress.ip_address(ip)
                    return ip
                except ValueError:
                    continue
        
        return 'unknown'
    
    def is_suspicious_user_agent(self, user_agent: str) -> bool:
        """Check if user agent looks suspicious."""
        suspicious_agents = [
            'sqlmap',
            'nikto',
            'nessus',
            'burpsuite',
            'scanner',
        ]
        
        user_agent_lower = user_agent.lower()
        return any(agent in user_agent_lower for agent in suspicious_agents)


class IPBlockingMiddleware(MiddlewareMixin):
    """
    Middleware to block suspicious IP addresses.
    """
    
    def __init__(self, get_response: Callable):
        super().__init__(get_response)
        self.blocked_ips = set()
        self.get_response = get_response
    
    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Block requests from blacklisted IPs."""
        ip = self.get_client_ip(request)
        
        # Check if IP is blocked (with error handling for cache)
        try:
            if ip in self.blocked_ips or cache.get(f'blocked_ip:{ip}'):
                security_logger.error(f"Blocked request from {ip} to {request.path}")
                return HttpResponse('Access Denied', status=403)
            
            # Check for too many failed attempts
            failed_attempts = cache.get(f'failed_attempts:{ip}', 0)
            if failed_attempts >= 10:  # Block after 10 failed attempts
                cache.set(f'blocked_ip:{ip}', True, 3600)  # Block for 1 hour
                security_logger.error(f"IP {ip} blocked due to too many failed attempts")
                return HttpResponse('Access Denied', status=403)
        except Exception as e:
            # Cache unavailable, continue without blocking (log the error)
            security_logger.warning(f"Cache unavailable for IP blocking: {e}")
        
        return None
    
    def process_response(self, request: HttpRequest, response: HttpResponse) -> HttpResponse:
        """Track failed attempts."""
        ip = self.get_client_ip(request)
        
        # Track failed login attempts (with error handling for cache)
        try:
            if (response.status_code in [401, 403] and 
                request.path in ['/api/accounts/login/', '/admin/login/']):
                
                failed_attempts = cache.get(f'failed_attempts:{ip}', 0) + 1
                cache.set(f'failed_attempts:{ip}', failed_attempts, 3600)  # 1 hour
                
                security_logger.warning(
                    f"Failed login attempt #{failed_attempts} from {ip}"
                )
            
            # Reset failed attempts on successful login
            elif (response.status_code == 200 and 
                  request.path in ['/api/accounts/login/', '/admin/login/']):
                cache.delete(f'failed_attempts:{ip}')
        except Exception as e:
            # Cache unavailable, log but continue
            security_logger.warning(f"Cache unavailable for tracking attempts: {e}")
        
        return response
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """Get the real client IP address."""
        # Same implementation as RequestLoggingMiddleware
        headers_to_check = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CF_CONNECTING_IP',
            'REMOTE_ADDR',
        ]
        
        for header in headers_to_check:
            ip = request.META.get(header)
            if ip:
                ip = ip.split(',')[0].strip()
                try:
                    ipaddress.ip_address(ip)
                    return ip
                except ValueError:
                    continue
        
        return 'unknown'


class APIRateLimitMiddleware(MiddlewareMixin):
    """
    Simple rate limiting middleware for API endpoints.
    For production, consider using django-ratelimit or similar.
    """
    
    def process_request(self, request: HttpRequest) -> HttpResponse | None:
        """Apply rate limiting to API requests."""
        if not request.path.startswith('/api/'):
            return None
        
        ip = self.get_client_ip(request)
        cache_key = f'api_requests:{ip}'
        
        try:
            # Get current request count
            requests = cache.get(cache_key, 0)
            
            # API rate limits
            if request.user.is_authenticated:
                max_requests = 1000  # 1000 requests per minute for authenticated users
            else:
                max_requests = 100   # 100 requests per minute for anonymous users
            
            if requests >= max_requests:
                security_logger.warning(
                    f"Rate limit exceeded for {ip}: {requests}/{max_requests}"
                )
                return HttpResponse(
                    'Rate limit exceeded. Please try again later.',
                    status=429,
                    content_type='application/json'
                )
            
            # Increment counter
            cache.set(cache_key, requests + 1, 60)  # Reset every minute
        except Exception as e:
            # Cache unavailable, allow request but log warning
            security_logger.warning(f"Cache unavailable for rate limiting: {e}")
        
        return None
    
    def get_client_ip(self, request: HttpRequest) -> str:
        """Get the real client IP address."""
        headers_to_check = [
            'HTTP_X_FORWARDED_FOR',
            'HTTP_X_REAL_IP',
            'HTTP_CF_CONNECTING_IP',
            'REMOTE_ADDR',
        ]
        
        for header in headers_to_check:
            ip = request.META.get(header)
            if ip:
                ip = ip.split(',')[0].strip()
                try:
                    ipaddress.ip_address(ip)
                    return ip
                except ValueError:
                    continue
        
        return 'unknown'