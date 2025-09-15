"""
Management command to create default groups and configure permissions.

This module provides a Django management command that creates default user groups
and configures their permissions based on JSON configuration files.
"""

import json
import logging
import os

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from django.core.management.base import BaseCommand

from drf_base_apps.core.abstract.constants import GroupChoices

logger = logging.getLogger(__name__)

DEFAULT_GROUPS = [choice.value for choice in GroupChoices]

DEFAULT_PERMISSIONS_FILE = settings.DEFAULT_PERMISSIONS_PATH or os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "fixtures", "default_permissions.json"
)


class Command(BaseCommand):
    """Management command to create default groups and configure permissions."""

    help = "Cria grupos padrão e configura permissões baseadas em JSON"

    def __init__(self, *args, **options):
        """Initialize the management command."""
        super().__init__(*args, **options)
        self.all_groups = Group.objects.all().prefetch_related("permissions")
        self.all_permissions = Permission.objects.all()

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--json-file", type=str, help="Caminho para arquivo JSON com configurações de permissões", required=False
        )
        parser.add_argument("--exists-ok", type=bool, help="Ignorar grupos já criados", required=False)

    def handle(self, *args, **options):
        """Handle the command execution."""
        json_file = options.get("json_file")
        exists_ok = options.get("exists_ok")

        if json_file and os.path.exists(json_file):
            with open(json_file) as f:
                permissions_config = json.load(f)
        else:
            # Carrega as permissões padrão do arquivo JSON
            try:
                if os.path.exists(DEFAULT_PERMISSIONS_FILE):
                    with open(DEFAULT_PERMISSIONS_FILE) as f:
                        permissions_config = json.load(f)
                    logger.info(f"Permissões padrão carregadas de {DEFAULT_PERMISSIONS_FILE}")
                else:
                    logger.warning(f"Arquivo de permissões padrão não encontrado: {DEFAULT_PERMISSIONS_FILE}")
                    permissions_config = {}
            except Exception as e:
                logger.error(f"Erro ao carregar permissões padrão: {e!s}", exc_info=True)
                permissions_config = {}

        self.create_groups(permissions_config, exists_ok)

    def create_groups(self, permissions_config, exists_ok):
        """Cria grupos e configura permissões baseadas na estrutura JSON."""
        for group_name in DEFAULT_GROUPS:
            group, created = self.all_groups.get_or_create(name=group_name)

            if created:
                self.stdout.write(self.style.SUCCESS(f'Grupo "{group_name}" criado com sucesso'))
            else:
                if exists_ok:
                    continue
                self.stdout.write(f'Grupo "{group_name}" já existe')

            if group_name in permissions_config:
                self.configure_group_permissions(group, permissions_config[group_name])

    def configure_group_permissions(self, group, group_config):
        """Configura permissões para um grupo específico baseado na configuração."""
        group.permissions.clear()

        for app_name, app_config in group_config.get("apps", {}).items():
            try:
                app_models = apps.get_app_config(app_name).get_models()

                for model in app_models:
                    model_name = model._meta.model_name
                    content_type = ContentType.objects.get_for_model(model)

                    crud_map = {
                        "create": f"add_{model_name}",
                        "read": f"view_{model_name}",
                        "update": f"change_{model_name}",
                        "delete": f"delete_{model_name}",
                    }

                    for crud_op, permission_name in crud_map.items():
                        if app_config.get(crud_op, False):
                            try:
                                perm = self.all_permissions.filter(
                                    codename=permission_name, content_type=content_type
                                ).first()
                                if not perm:
                                    raise Permission.DoesNotExist
                                group.permissions.add(perm)
                                self.stdout.write(f'Adicionada permissão "{permission_name}" ao grupo "{group.name}"')
                            except Permission.DoesNotExist:
                                self.stdout.write(
                                    self.style.WARNING(
                                        f'Permissão "{permission_name}" não encontrada para {model_name}'
                                    )
                                )
            except LookupError:
                self.stdout.write(self.style.WARNING(f'App "{app_name}" não encontrado'))

    def export_permissions_to_json(self, file_path):
        """Exporta configuração atual de permissões para um arquivo JSON."""
        current_config = {}

        for group_name in DEFAULT_GROUPS:
            try:
                group = self.all_groups.filter(name=group_name).first()
                group_config = {"apps": {}}

                for perm in group.permissions.all():
                    app_label = perm.content_type.app_label

                    if app_label not in group_config["apps"]:
                        group_config["apps"][app_label] = {
                            "create": False,
                            "read": False,
                            "update": False,
                            "delete": False,
                        }

                    if perm.codename.startswith("add_"):
                        group_config["apps"][app_label]["create"] = True
                    elif perm.codename.startswith("view_"):
                        group_config["apps"][app_label]["read"] = True
                    elif perm.codename.startswith("change_"):
                        group_config["apps"][app_label]["update"] = True
                    elif perm.codename.startswith("delete_"):
                        group_config["apps"][app_label]["delete"] = True

                current_config[group_name] = group_config
            except Group.DoesNotExist:
                pass

        with open(file_path, "w") as f:
            json.dump(current_config, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f"Configuração de permissões exportada para {file_path}"))
