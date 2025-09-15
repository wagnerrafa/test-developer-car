"""Permission classes for API access control."""

from django.utils.translation import gettext_lazy as _
from rest_framework.permissions import BasePermission

from drf_base_config.settings import ENV_DEV, SWAGGER_URL


class CheckHasPermission(BasePermission):
    """
    Check if the user has the correct permission to access the requested view.

    Attributes:
        None

    Methods:
        has_permission(request, view):
            Check if the user has permission to access the requested view.

    Args:
                request: the HTTP request object
                view: the view being accessed

    Returns:
                True if the user has permission, False otherwise

    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        Returns:
            True if the user has permission, False otherwise

        """
        option = {
            "GET": "view",
            "PUT": "change",
            "POST": "add",
            "DELETE": "delete",
        }

        return request.user.has_permission(f"{option.get(request.method)}_{view.model.__name__.lower()}")


class CheckPermissions(BasePermission):
    """
    Permission check for allowing a user to change steps in a process.

    Methods:
        - has_permission(self, request, view): Checks if the requesting user has permission to change the process step.

    """

    message = _("You do not have permission. Contact admin")

    def has_permission(self, request, view):
        """
        Check if the user has permission to change the step of a Calculation object.

        Receives request and view objects as parameters. It gets the calculation_id from the view,
        checks if the user has the necessary permission codename, and returns a boolean indicating
        if the user has permission or not. If the user doesn't have permission, it raises a
        ValidationError with a message indicating the current and next steps that cannot be changed.
        """
        if hasattr(view, "perms") is False:
            raise AttributeError(_('Need to add "perms: list" attribute to use CheckPermissions class'))
        perms = view.perms
        return request.user.has_permission(perms)


class NotSwaggerPermission(BasePermission):
    """
    Check if the user has the correct permission to access the requested view.

    Methods:
        has_permission(request, view):
            Check if the user has permission to access the requested view.

    Args:
                request: the HTTP request object
                view: the view being accessed

    Returns:
                True if the user has permission, False otherwise

    """

    def has_permission(self, request, view):
        """
        Check if the user has permission to access the requested view.

        Args:
            request: the HTTP request object
            view: the view being accessed

        Returns:
            True if the user has permission, False otherwise

        """
        return not (request.path == SWAGGER_URL and not ENV_DEV)


def check_query_permission(perms):
    """Check query permissions with a decorator."""

    def decorator(func):
        def wrapper(self, *args, **kwargs):
            has_perm = self.request.user.has_permission(perms)
            if has_perm:
                return {}
            return func(self, *args, **kwargs)

        return wrapper

    return decorator
