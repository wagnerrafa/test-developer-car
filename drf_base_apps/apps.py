"""
Configuração do app drf_base_apps.

Este módulo define a configuração do app drf_base_apps,
incluindo o tipo de campo para chaves primárias.
"""

from django.apps import AppConfig


class DrfBaseAppsConfig(AppConfig):
    """
    Configuração do app drf_base_apps.

    Define as configurações padrão para o app drf_base_apps,
    incluindo o tipo de campo para chaves primárias.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps"


def utils():
    """Return utility placeholder value."""
    return None
