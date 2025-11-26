"""Apps configuration for orders."""

from django.apps import AppConfig


class OrdersConfig(AppConfig):
    """Configuration for orders app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.orders'
    verbose_name = 'Orders'

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here to avoid circular imports
        pass