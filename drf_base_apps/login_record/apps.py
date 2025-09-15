"""App configuration for login record."""

from django.apps import AppConfig


class LoginRecordConfig(AppConfig):
    """Configuration class for the login record Django app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.login_record"
