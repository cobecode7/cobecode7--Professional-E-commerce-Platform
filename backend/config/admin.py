"""
Custom Django Admin Configuration
Enhances the default admin interface with custom styling and functionality
"""
from django.contrib import admin
from django.contrib.admin import AdminSite
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html


class EcommerceAdminSite(AdminSite):
    """Custom Admin Site with enhanced branding and functionality."""
    
    # Site header and branding
    site_header = _('E-Commerce Platform Administration')
    site_title = _('E-Commerce Admin')
    index_title = _('E-Commerce Platform Dashboard')
    
    # Custom styling
    enable_nav_sidebar = True
    
    def each_context(self, request):
        """
        Return a dictionary of variables to put in the template context for
        *every* page in the admin site.
        """
        context = super().each_context(request)
        context.update({
            'site_url': '/',
            'has_permission': request.user.is_active and request.user.is_staff,
            'available_apps': self.get_app_list(request),
        })
        return context

    def index(self, request, extra_context=None):
        """
        Display the main admin index page, which lists all of the installed
        apps that have been registered in this site.
        """
        extra_context = extra_context or {}
        
        # Add custom dashboard stats
        try:
            from apps.accounts.models import CustomUser
            from apps.products.models import Product
            from apps.orders.models import Order
            
            stats = {
                'total_users': CustomUser.objects.count(),
                'total_products': Product.objects.count(),
                'active_products': Product.objects.filter(is_active=True).count(),
                'total_orders': Order.objects.count() if hasattr(Order.objects, 'count') else 0,
            }
            extra_context['dashboard_stats'] = stats
        except Exception as e:
            # Gracefully handle missing models during migrations
            extra_context['dashboard_stats'] = None
            
        return super().index(request, extra_context)