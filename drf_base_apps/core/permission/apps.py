"""App configuration for permission management."""

from django.apps import AppConfig

from drf_base_apps.utils import _


class PermissionConfig(AppConfig):
    """Configuration class for the permission Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.core.permission"
    verbose_name = _("Permission")
