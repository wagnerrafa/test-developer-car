"""Custom user manager for the application."""

from django.contrib.auth.models import UserManager


class CustomUserManager(UserManager):
    """Custom user manager that disables certain operations for security."""

    def create_superuser(self, username, email=None, password=None, **extra_fields):
        """Disable superuser creation for security reasons."""
        raise ValueError("Superuser creation is disabled.")

    def bulk_create(self, objs, batch_size=None, ignore_conflicts=False):
        """Disable bulk creation for security reasons."""
        raise ValueError("Bulk creation is disabled.")

    def bulk_update(self, objs, fields, batch_size=None):
        """Disable bulk update for security reasons."""
        raise ValueError("Bulk update is disabled.")

    def create_user(self, username, email=None, password=None, **extra_fields):
        """Create a regular user with default settings."""
        extra_fields["is_staff"] = False
        extra_fields["is_active"] = False
        return self._create_user(username, email, password, **extra_fields)
