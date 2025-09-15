"""
Constants for the abstract core module.

This module defines constants used throughout the abstract core functionality,
including URI defaults and group choices for user management.
"""

from django.db import models
from django.utils.translation import gettext_lazy as _

APP_NAME = "ABSTRACT"


class URIDefault:
    """Default URI constants for the application."""

    USER = "user"


class GroupChoices(models.TextChoices):
    """Choices para grupos de usuários no sistema."""

    USER = "USER", _("USER")
