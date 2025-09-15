"""App configuration for security."""

from django.apps import AppConfig


class SecurityConfig(AppConfig):
    """Configuration class for the security Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.security"
