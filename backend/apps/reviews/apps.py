"""Apps configuration for reviews."""

from django.apps import AppConfig


class ReviewsConfig(AppConfig):
    """Configuration for reviews app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.reviews'
    verbose_name = 'Reviews'

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here to avoid circular imports
        pass