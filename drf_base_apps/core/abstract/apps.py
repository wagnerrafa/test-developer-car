"""
Configuração do app abstract.

Este módulo define a configuração do app abstract,
incluindo registro automático de modelos no admin.
"""

from django.apps import AppConfig, apps
from django.contrib import admin
from django.db import models

from drf_base_apps.utils import _
from drf_base_config.settings import AUTO_REGISTER_MODELS


class AbstractConfig(AppConfig):
    """
    Configuração do app abstract.

    Define as configurações padrão para o app abstract,
    incluindo registro automático de modelos no admin.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "drf_base_apps.core.abstract"
    verbose_name = _("Abstract User")

    def ready(self):
        """
        Registra todos os apps que herdam da classe AbstractModel.

        Adiciona campos padrão e lista de campos de busca para
        todos os modelos que herdam de AbstractModel.
        """
        if AUTO_REGISTER_MODELS:
            from drf_base_apps.core.abstract.models import AbstractModel

            for model in apps.get_models():
                if issubclass(model, AbstractModel) and admin.site.is_registered(model):
                    admin_get = admin.site._registry[model]
                    if str(admin_get).endswith(".ModelAdmin"):
                        admin.site.unregister(model)

                        class AbstractModelAdmin(admin.ModelAdmin):
                            list_display = (
                                "__str__",
                                "id",
                                "created_at",
                                "updated_at",
                            )
                            readonly_fields = ("created_at", "updated_at", "id", "create_user", "update_user")
                            search_fields = get_fields(model)

                        admin.site.register(model, AbstractModelAdmin)
                    else:
                        admin_get.list_display = list(
                            {"__str__", "id", "created_at", "updated_at", *list(admin_get.list_display)}
                        )
                        admin_get.readonly_fields = list(
                            {
                                "created_at",
                                "updated_at",
                                "id",
                                "create_user",
                                "update_user",
                                *list(admin_get.readonly_fields),
                            }
                        )
                        admin_get.search_fields = get_fields(model)


def get_fields(model):
    """Get a list fields of model obj."""
    from django.contrib.contenttypes.fields import GenericForeignKey

    return [
        field.name
        for field in model._meta.get_fields()
        if not field.is_relation
        or not isinstance(
            field,
            (models.OneToOneField, models.ManyToManyField, models.ManyToOneRel, models.ForeignKey, GenericForeignKey),
        )
    ]
