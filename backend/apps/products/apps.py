"""Apps configuration for products."""

from django.apps import AppConfig


class ProductsConfig(AppConfig):
    """Configuration for products app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.products'
    verbose_name = 'Products'

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here to avoid circular imports
        pass