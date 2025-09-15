"""Common methods."""

import secrets

from django.contrib.auth import get_user_model as md
from django.urls import reverse
from django.utils.translation import gettext_lazy


def _(text):
    """
    Translate the given text using gettext_lazy.

    :param text: The text to be translated.
    :type text: str
    :return: The translated text.
    :rtype: str
    """
    return gettext_lazy(text)


def doc(docstring):
    """
    Set the docstring of a function or method.

    :param docstring: The docstring to be set.
    :type docstring: str
    :return: The decorated function or method.
    :rtype: function
    """

    def decorate(fn):
        fn.__doc__ = _(docstring)
        return fn

    return decorate


class AttrDict(dict):
    """
    A dictionary subclass that allows attribute-style access to its elements.

    This class inherits from the built-in `dict` class and overrides the `__getattr__`
    and `__setattr__` methods to enable accessing dictionary elements as attributes.

    Example usage:
     Note: If an attribute does not exist, it will raise a `KeyError`.

    :param dict: The initial dictionary to populate the `AttrDict`.
    :type dict: dict
    """

    def __getattr__(self, attr):
        """Get an attribute from the dictionary."""
        return self[attr]

    def __setattr__(self, attr, value):
        """Set an attribute in the dictionary."""
        self[attr] = value


def secret_number(min_value: int, max_value: int):
    """
    Generate a random secret number within the given range.

    This function generates a random secret number between `min_value` and `max_value`,
    inclusive. It uses the `secrets.randbelow()` function from the `secrets` module.

    :param min_value: The minimum value of the range.
    :type min_value: int
    :param max_value: The maximum value of the range.
    :type max_value: int
    :return: The randomly generated secret number.
    :rtype: int
    """
    min_ = min(min_value, max_value)
    max_ = max(min_value, max_value)
    return secrets.randbelow(max_ - min_) + 1


def get_user_model():
    """Get the User Model defined in settings."""
    return md()


def get_url_from_name(name, kwargs=None):
    """Get full url by name."""
    if not kwargs:
        kwargs = {}
    return reverse(name, kwargs=kwargs)
