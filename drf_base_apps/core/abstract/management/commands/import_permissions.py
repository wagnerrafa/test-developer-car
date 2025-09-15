"""
Management command to import permissions configuration.

This module provides a Django management command that imports permissions
configuration from a JSON file to update group permissions.
"""

import json
import os

from django.core.management.base import BaseCommand

from drf_base_apps.core.abstract.permissions import GroupPermissionManager


class Command(BaseCommand):
    """Management command to import permissions configuration."""

    help = "Importa configuração de permissões de um arquivo JSON"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--input", type=str, required=True, help="Caminho para o arquivo JSON com configurações de permissões"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        input_file = options.get("input")

        if not os.path.exists(input_file):
            self.stdout.write(self.style.ERROR(f"Arquivo {input_file} não encontrado"))
            return

        with open(input_file) as f:
            config = json.load(f)

        manager = GroupPermissionManager(input_file)

        for group_name, group_config in config.items():
            for app_name, app_permissions in group_config.get("apps", {}).items():
                success = manager.set_group_permissions(group_name, app_name, app_permissions)

                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f"Permissões para {group_name}/{app_name} atualizadas com sucesso")
                    )
                else:
                    self.stdout.write(self.style.WARNING(f"Falha ao atualizar permissões para {group_name}/{app_name}"))

        self.stdout.write(self.style.SUCCESS(f"Configuração de permissões importada de {input_file}"))
