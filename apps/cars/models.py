"""
Defines models for car management system.

Inherits from AbstractModel, which provides common fields such as id, created_at,
and updated_at. Models include Brand and Car with specific fields
for automotive management.
"""

from django.core.validators import MaxValueValidator, MinValueValidator, RegexValidator
from django.db import models

from drf_base_apps.models import AbstractDescription
from drf_base_apps.utils import _

from .constants import FuelTypeChoices, TransmissionChoices
from .utils import normalize_name


class AbstractNameModel(AbstractDescription):
    """
    Abstract model that provides a normalized name field.

    This model can be extended by other models to add a name field
    with automatic normalization and common behavior.
    """

    name = models.CharField(_("Name"), max_length=100, unique=True)

    class Meta:
        """Meta options for AbstractNameModel."""

        abstract = True
        ordering = ("name",)

    def save(self, *args, **kwargs):
        """Save the model with normalized name."""
        self.name = normalize_name(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of the model."""
        return self.name


class Brand(AbstractNameModel):
    """
    A class representing a car brand.

    Attributes:
        name (str): Brand name

    """

    class Meta:
        """Meta options for Brand model."""

        verbose_name = _("Brand")
        verbose_name_plural = _("Brands")


class Color(AbstractNameModel):
    """
    A class representing a car color.

    Attributes:
        name (str): Color name

    """

    name = models.CharField(_("Name"), max_length=50, unique=True)

    class Meta:
        """Meta options for Color model."""

        verbose_name = _("Color")
        verbose_name_plural = _("Colors")


class Engine(AbstractNameModel):
    """
    A class representing a car engine.

    Attributes:
        name (str): Engine name/specification
        displacement (str): Engine displacement (e.g., 1.0, 1.6, 2.0)
        power (int): Engine power in horsepower

    """

    displacement = models.CharField(_("Displacement"), max_length=20)
    power = models.IntegerField(
        _("Power (HP)"), validators=[MinValueValidator(1)], help_text=_("Engine power in horsepower")
    )

    class Meta:
        """Meta options for Engine model."""

        verbose_name = _("Engine")
        verbose_name_plural = _("Engines")

    def save(self, *args, **kwargs):
        """Save the engine with normalized displacement."""
        self.displacement = normalize_name(self.displacement)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of the engine."""
        return f"{self.name} ({self.displacement})"


class CarName(AbstractDescription):
    """
    A class representing a car name/title.

    Attributes:
        name (str): Car name/title
        brand (Brand): Associated brand

    """

    name = models.CharField(_("Name"), max_length=200, unique=True)
    brand = models.ForeignKey(Brand, on_delete=models.PROTECT, related_name="car_names", verbose_name=_("Brand"))

    class Meta:
        """Meta options for CarName model."""

        verbose_name = _("Car Name")
        verbose_name_plural = _("Car Names")
        ordering = ("brand__name", "name")
        unique_together = ("name", "brand")

    def save(self, *args, **kwargs):
        """Save the car name with normalized name."""
        self.name = normalize_name(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        """Return string representation of the car name."""
        return f"{self.brand.name} {self.name}"


class CarModel(AbstractNameModel):
    """
    A class representing a car model.

    Attributes:
        name (str): Model name

    """

    class Meta:
        """Meta options for CarModel model."""

        verbose_name = _("Car Model")
        verbose_name_plural = _("Car Models")


class Car(AbstractDescription):
    """
    A class representing a Car.

    Attributes:
        car_name (CarName): Car name/title
        car_model (CarModel): Car model
        year (int): Manufacturing year
        engine (Engine): Engine specification
        fuel_type (str): Type of fuel
        color (Color): Car color
        mileage (int): Mileage in kilometers
        doors (int): Number of doors
        transmission (str): Transmission type
        price (float): Car price

    """

    car_name = models.ForeignKey(CarName, on_delete=models.PROTECT, related_name="cars", verbose_name=_("Car Name"))
    car_model = models.ForeignKey(CarModel, on_delete=models.PROTECT, related_name="cars", verbose_name=_("Car Model"))
    year_manufacture = models.IntegerField(
        _("Year Manufacture"),
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(9999),
            RegexValidator(regex=r"^\d{4}$", message=_("Year must be exactly 4 digits.")),
        ],
    )
    year_model = models.IntegerField(
        _("Year Model"),
        validators=[
            MinValueValidator(1900),
            MaxValueValidator(9999),
            RegexValidator(regex=r"^\d{4}$", message=_("Year must be exactly 4 digits.")),
        ],
    )
    engine = models.ForeignKey(Engine, on_delete=models.PROTECT, related_name="cars", verbose_name=_("Engine"))
    fuel_type = models.CharField(_("Fuel Type"), max_length=20, choices=FuelTypeChoices)
    color = models.ForeignKey(Color, on_delete=models.PROTECT, related_name="cars", verbose_name=_("Color"))
    mileage = models.IntegerField(_("Mileage"), validators=[MinValueValidator(0)], help_text=_("Mileage in kilometers"))
    doors = models.IntegerField(_("Doors"), validators=[MinValueValidator(2), MaxValueValidator(8)])
    transmission = models.CharField(_("Transmission"), max_length=20, choices=TransmissionChoices)
    price = models.FloatField(_("Price"), validators=[MinValueValidator(0.01)])

    class Meta:
        """Meta options for Car model."""

        verbose_name = _("Car")
        verbose_name_plural = _("Cars")
        ordering = ("-created_at", "car_model__name")

    def __str__(self):
        """Return string representation of the car."""
        return f"{self.car_name} ({self.year})"
