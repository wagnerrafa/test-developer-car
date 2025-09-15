"""
Abstract models for the DRF base applications.

This module provides abstract model classes that can be extended by other applications
to provide common functionality and fields.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

from drf_base_apps.core.abstract.models import AbstractModel


class AbstractDescription(AbstractModel):
    """
    Abstract model that provides a description field.

    This model can be extended by other models to add a description field
    with internationalization support.
    """

    description = models.CharField(_("Description"), max_length=150)

    class Meta:
        """Meta options for AbstractDescription model."""

        abstract = True

    def __str__(self):
        """Return the string representation of the model."""
        return self.description
