"""Utility functions for the cars app."""

import re
import unicodedata


def normalize_name(name):
    """
    Normalize a name by applying standard formatting rules.

    Rules applied:
    - Remove extra whitespace
    - Convert to title case
    - Remove special characters except spaces and hyphens
    - Normalize unicode characters

    Args:
        name (str): The name to normalize

    Returns:
        str: The normalized name

    """
    if not name:
        return name

    # Remove extra whitespace and strip
    name = " ".join(name.split())

    # Normalize unicode characters
    name = unicodedata.normalize("NFD", name)

    # Convert to title case
    name = name.title()

    # Remove special characters except spaces, hyphens, and parentheses
    name = re.sub(r"[^\w\s\-\(\)]", "", name)

    # Clean up multiple spaces
    name = " ".join(name.split())

    return name.strip()


def normalize_car_name(brand_name, model_name, year):
    """
    Create a standardized car name from brand, model and year.

    Args:
        brand_name (str): Brand name
        model_name (str): Model name
        year (int): Manufacturing year

    Returns:
        str: Standardized car name

    """
    brand = normalize_name(brand_name) if brand_name else ""
    model = normalize_name(model_name) if model_name else ""

    if brand and model:
        return f"{brand} {model} {year}"
    elif brand:
        return f"{brand} {year}"
    elif model:
        return f"{model} {year}"
    else:
        return str(year)
