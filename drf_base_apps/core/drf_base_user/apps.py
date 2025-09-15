"""App configuration for the drf_base_user module."""

from django.apps import AppConfig

from drf_base_apps.utils import _


class BaseUserConfig(AppConfig):
    """Configuration class for the drf_base_user Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.core.drf_base_user"
    verbose_name = _("BaseUser")
