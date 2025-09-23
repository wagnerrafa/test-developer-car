"""
Django AppConfig class for configuring the 'car' app.

The CarConfig class inherits from the AppConfig class and sets the default_auto_field
attribute to 'django.db.models.BigAutoField' to use a Big Integer field as the primary key
for all models by default. The name attribute is set to 'car', which is the name of the app
this configuration belongs to.

Attributes:
    default_auto_field: A string representing the default primary key field type for all models
    name: A string representing the name of the app

"""

from django.apps import AppConfig

from drf_base_apps.utils import _


class CarConfig(AppConfig):
    """Configuration for the cars app."""

    default_auto_field = "django.db.models.BigAutoField"
    name = "apps.cars"
    verbose_name = _("Car")
    verbose_plural_name = _("Cars")
