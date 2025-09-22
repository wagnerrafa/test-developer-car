"""
Django app configuration for WebSocket functionality.

This module configures the WebSocket application and handles automatic
discovery of socket modules across installed apps.
"""

from importlib import import_module

from django.apps import AppConfig
from django.conf import settings


class WebSocketsConfig(AppConfig):
    """Configuration for the WebSocket application."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.web_sockets"

    def ready(self):
        """Initialize the app and discover socket modules."""
        # Auto Discover modules to sockets
        for app in settings.INSTALLED_APPS:
            try:
                import_module(f"{app}.sockets")
            except (AttributeError, ModuleNotFoundError):
                continue
