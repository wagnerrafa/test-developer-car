"""Forms for user management."""

from django.contrib.auth.forms import UsernameField
from django.forms import ModelForm

from .models import User


class UserCreationForm(ModelForm):
    """
    A form that creates a user, with no privileges, from the given username and password.

    This form provides a simple way to create user accounts with basic information
    including username, first name, last name, and email.
    """

    class Meta:
        """Meta options for UserCreationForm."""

        model = User
        fields = ("username", "first_name", "last_name", "email")
        field_classes = {"username": UsernameField}

    def __init__(self, *args, **kwargs):
        """Initialize the form with autofocus on username field."""
        super().__init__(*args, **kwargs)
        if self._meta.model.USERNAME_FIELD in self.fields:
            self.fields[self._meta.model.USERNAME_FIELD].widget.attrs["autofocus"] = True
