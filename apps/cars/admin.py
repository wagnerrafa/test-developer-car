"""
Registers the Car models with the Django admin site.

This file facilitates the registration of the Car models with the Django admin site.
By importing the admin module from the django.contrib package and the relevant models from the car.models module,
this code registers the models with the admin site for easy management.

Usage:
- Import this file in the Django project's admin.py file to register the models with the admin site.

Example:
# In admin.py
from django.contrib import admin

admin.site.register(Car)

"""

from django.contrib import admin

from apps.cars.models import Brand, Car, CarModel, CarName, Color, Engine
from drf_base_apps.core.abstract.admin import AbstractAdmin


@admin.register(Car)
class CarAdmin(AbstractAdmin):
    """Car model admin class."""

    pass


@admin.register(Brand)
class BrandAdmin(AbstractAdmin):
    """Brand model admin class."""

    pass


@admin.register(Color)
class ColorAdmin(AbstractAdmin):
    """Color model admin class."""

    pass


@admin.register(Engine)
class EngineAdmin(AbstractAdmin):
    """Engine model admin class."""

    pass


@admin.register(CarName)
class CarNameAdmin(AbstractAdmin):
    """CarName model admin class."""

    pass


@admin.register(CarModel)
class CarModelAdmin(AbstractAdmin):
    """CarModel model admin class."""

    pass
