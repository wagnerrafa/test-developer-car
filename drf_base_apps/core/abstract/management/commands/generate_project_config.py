"""
Comando Django para gerar arquivos de configuração baseados nos templates.

Este comando usa o startapp do Django com templates personalizados
para criar novos projetos baseados no drf_base_apps.
"""

import logging
import os
import shutil
from pathlib import Path

from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError

import drf_base_apps


class Command(BaseCommand):
    """Comando para gerar configurações de projeto Django."""

    help = """
    Gera arquivos de configuração Django baseados nos templates.

    Exemplo de uso:
        python manage.py generate_project_config --project-name=meu_projeto
        python manage.py generate_project_config --project-name=meu_projeto --output-dir=/path/to/output
    """

    def add_arguments(self, parser):
        """Adiciona argumentos ao comando."""
        parser.add_argument("--project-name", type=str, required=True, help="Nome do projeto Django (obrigatório)")
        parser.add_argument("--output-dir", type=str, default=".", help="Diretório de saída (padrão: diretório atual)")
        parser.add_argument("--force", action="store_true", help="Força a sobrescrita de arquivos existentes")

    def handle(self, *args, **options):
        """Executa o comando."""
        project_name = options["project_name"]
        output_dir = Path(options["output_dir"]).resolve()
        force = options["force"]

        template_path = Path(drf_base_apps.__file__).parent / "app_settings_template"

        if not template_path.exists():
            raise CommandError(f"Diretório de templates padrão não encontrado: {template_path}")

        # Cria o diretório de saída se não existir
        output_dir.mkdir(parents=True, exist_ok=True)

        self.stdout.write(self.style.SUCCESS(f"🚀 Gerando configurações para o projeto: {project_name}"))
        self.stdout.write(f"📁 Diretório de saída: {output_dir}")
        self.stdout.write(f"📋 Diretório de templates: {template_path}")

        try:
            # Usa o startapp do Django com template personalizado
            self._generate_project_with_startapp(project_name, template_path, output_dir, force)

            self.stdout.write(self.style.SUCCESS(f"✅ Configurações geradas com sucesso em: {output_dir}"))
            self.stdout.write(
                self.style.WARNING("⚠️  Lembre-se de ajustar as configurações conforme necessário para seu projeto!")
            )

        except Exception as e:
            raise CommandError(f"Erro ao gerar configurações: {e!s}") from e

    def _generate_project_with_startapp(self, project_name, template_path, output_dir, force):
        """Gera o projeto usando startapp com template personalizado."""
        app_name = f"{project_name}_config"
        project_path = output_dir / app_name
        project_tmp_path = output_dir / f"tmp_{project_name}"

        try:
            # Chama o startapp com template personalizado no diretório do projeto
            call_command("startapp", app_name, template=str(template_path), verbosity=0)  # Reduz output verboso

            # Move os arquivos do subdiretório para o diretório principal do projeto
            shutil.move(project_path, project_tmp_path)

            if project_tmp_path.exists():
                for item in os.listdir(project_tmp_path):
                    caminho_origem = os.path.join(project_tmp_path, item)
                    caminho_destino = os.path.join(output_dir, item)

                    if not os.path.exists(caminho_destino) or force:
                        shutil.move(caminho_origem, caminho_destino)

                shutil.rmtree(project_tmp_path)
                self.stdout.write(f"✅ Arquivos movidos para o diretório principal: {project_path}")

            self.stdout.write(f"✅ Projeto gerado com startapp: {project_path}")

        except Exception as e:
            logging.error(e, exc_info=True)
            raise CommandError(f"Erro ao executar startapp: {e!s}") from e
