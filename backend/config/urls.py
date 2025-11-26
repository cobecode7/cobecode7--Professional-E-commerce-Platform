"""Main URL configuration."""
from django.contrib import admin
from django.urls import path, include
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView, SpectacularRedocView
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView
from django.http import JsonResponse

# Import and configure custom admin before URL patterns
try:
    from . import admin as custom_admin
except ImportError:
    # Handle missing admin configuration gracefully
    pass

# Simple API root view
def api_root(request):
    """API root endpoint with available endpoints."""
    return JsonResponse({
        'message': 'E-commerce Platform API',
        'version': '1.0.0',
        'endpoints': {
            'admin': '/admin/',
            'api_docs': '/api/docs/',
            'api_schema': '/api/schema/',
            'accounts': '/api/accounts/',
            'products': '/api/products/',
            'orders': '/api/orders/',
        }
    })

urlpatterns = [
    # Root redirect to API docs
    path('', RedirectView.as_view(url='/api/docs/', permanent=False)),
    
    # Admin
    path('admin/', admin.site.urls),
    
    # API Root
    path('api/', api_root, name='api-root'),
    
    # API Documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
    
    # API Endpoints
    path('api/accounts/', include('apps.accounts.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
