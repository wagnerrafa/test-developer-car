"""
Module: ValidationErrorAdapter.

This module provides a custom adaptation of validation errors for use in both Django
and Django REST Framework (DRF) contexts.

Classes:
- CustomAPIException: Custom API exception class that extends DRF's APIException.
                      It initializes with a detail message and an optional error code.

- ValidationErrorAdapter: A custom exception class that adapts Django's ValidationError
                           to be compatible with DRF's APIException. It inherits from both
                           Django's ValidationError and CustomAPIException.

Methods:
- CustomAPIException.__init__(self, *args, **kwargs):
  Initializes the CustomAPIException with a detail message and an optional error code.

- ValidationErrorAdapter.__init__(self, *args, **kwargs):
  Initializes the ValidationErrorAdapter with error details, code, and optional parameters.
  It adapts Django's ValidationError to extend CustomAPIException, ensuring compatibility
  with DRF's exception handling.

Usage:
To use ValidationErrorAdapter, raise instances of it when handling validation errors
in Django and DRF applications. This allows consistent error handling and messaging
across different parts of the application, enhancing maintainability and user experience.

"""

from django.core.exceptions import ValidationError
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_400_BAD_REQUEST


class CustomAPIException(APIException):
    """
    Custom exception class for API exceptions.

    Inherits:
        APIException: DRF's base exception class for API-related errors.

    Methods:
        __init__(self, *args, **kwargs):
            Initializes the exception with a detail message and an optional error code.

    """

    def __init__(self, *args, **kwargs):
        """Initialize the exception with a detail message and an optional error code."""
        super().__init__(detail=args[0], code=args[1])


class ValidationAdapterError(ValidationError, CustomAPIException):
    """
    Custom exception class that adapts Django's ValidationError to be compatible with DRF's APIException.

    Inherits:
        ValidationError: Django's base exception class for validation errors.
        CustomAPIException: Custom exception class for API exceptions.

    Methods:
        __init__(self, *args, **kwargs):
            Initialize the exception with error details, code, and optional parameters.
            Adapts Django's ValidationError to extend CustomAPIException.

    """

    def __init__(self, *args, **kwargs):
        """
        Initialize the exception with error details, code, and optional parameters.

        Adapts Django's ValidationError to extend CustomAPIException.
        """
        self.error_list = [self]
        self.detail = args
        self.message = args
        self.code = kwargs.get("code")
        self.status_code = HTTP_400_BAD_REQUEST
        self.params = kwargs.get("params")
        super().__init__(*args, **kwargs)
