"""App configuration for custom log viewer."""

from django.apps import AppConfig


class CustomLogViewerConfig(AppConfig):
    """Configuration class for the custom log viewer Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.custom_log_viewer"
