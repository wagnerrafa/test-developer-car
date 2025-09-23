"""Constants for the cars app."""

APP_NAME = "CAR"
from django.db import models

from drf_base_apps.core.abstract.constants import URIDefault
from drf_base_apps.utils import _


class CarURIs:
    """URI constants for Car endpoints."""

    USER = f"{URIDefault.USER}/car/"


class BrandURIs:
    """URI constants for Brand endpoints."""

    USER = f"{URIDefault.USER}/brand/"


class ColorURIs:
    """URI constants for Color endpoints."""

    USER = f"{URIDefault.USER}/color/"


class EngineURIs:
    """URI constants for Engine endpoints."""

    USER = f"{URIDefault.USER}/engine/"


class CarNameURIs:
    """URI constants for CarName endpoints."""

    USER = f"{URIDefault.USER}/car-name/"


class CarModelURIs:
    """URI constants for CarModel endpoints."""

    USER = f"{URIDefault.USER}/car-model/"


class FuelTypeChoices(models.TextChoices):
    """Choices for fuel type."""

    GASOLINE = "gasoline", _("Gasoline")
    ETHANOL = "ethanol", _("Ethanol")
    FLEX = "flex", _("Flex")
    DIESEL = "diesel", _("Diesel")
    ELECTRIC = "electric", _("Electric")
    HYBRID = "hybrid", _("Hybrid")


class TransmissionChoices(models.TextChoices):
    """Choices for transmission type."""

    MANUAL = "manual", _("Manual")
    AUTOMATIC = "automatic", _("Automatic")
    CVT = "cvt", _("CVT")
    SEMI_AUTOMATIC = "semi_automatic", _("Semi Automatic")
    DUAL_CLUTCH = "dual_clutch", _("Dual Clutch")
