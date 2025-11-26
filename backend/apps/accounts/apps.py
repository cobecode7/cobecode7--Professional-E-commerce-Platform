"""Apps configuration for accounts."""

from django.apps import AppConfig


class AccountsConfig(AppConfig):
    """Configuration for accounts app."""
    
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.accounts'
    verbose_name = 'User Accounts'

    def ready(self):
        """Import signals when app is ready."""
        # Import signals here to avoid circular imports
        pass