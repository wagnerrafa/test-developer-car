"""
Management command to export current permissions configuration.

This module provides a Django management command that exports the current
permissions configuration to a JSON file for backup or migration purposes.
"""

import json
import os

from django.core.management.base import BaseCommand

from drf_base_apps.core.abstract.permissions import GroupPermissionManager


class Command(BaseCommand):
    """Management command to export current permissions configuration."""

    help = "Exporta configuração atual de permissões para um arquivo JSON"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument(
            "--output", type=str, default="permissions_config.json", help="Caminho para o arquivo de saída JSON"
        )

    def handle(self, *args, **options):
        """Handle the command execution."""
        output_file = options.get("output")

        output_dir = os.path.dirname(output_file)
        if output_dir and not os.path.exists(output_dir):
            os.makedirs(output_dir)

        manager = GroupPermissionManager()
        current_config = manager.export_current_permissions()

        with open(output_file, "w") as f:
            json.dump(current_config, f, indent=4)

        self.stdout.write(self.style.SUCCESS(f"Configuração de permissões exportada para {output_file}"))
