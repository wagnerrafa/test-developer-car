"""
Management command for interactive permissions management.

This module provides a Django management command that offers an interactive
interface for managing group permissions and configurations.
"""

import json
import logging
import os
import sys

from django.apps import apps
from django.conf import settings
from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand

from drf_base_apps.core.abstract.permissions import GroupPermissionManager

logger = logging.getLogger(__name__)

RESET = "\033[0m"
BOLD = "\033[1m"
GREEN = "\033[32m"
BLUE = "\033[34m"
CYAN = "\033[36m"
YELLOW = "\033[33m"

from drf_base_apps.core.abstract.constants import GroupChoices

DEFAULT_GROUPS = [choice.value for choice in GroupChoices]


class Command(BaseCommand):
    """Management command for interactive permissions management."""

    help = "Interface interativa para gerenciar permissões de grupos"

    def add_arguments(self, parser):
        """Add command line arguments."""
        parser.add_argument("--config-file", type=str, help="Caminho para arquivo JSON com configurações de permissões")

    def handle(self, *args, **options):
        """Handle the command execution."""
        config_file = options.get("config_file")
        self.permission_manager = GroupPermissionManager(config_file)

        try:
            self.main_menu()
        except KeyboardInterrupt:
            self.stdout.write("\nSaindo do gerenciador de permissões...")
            sys.exit(0)

    def main_menu(self):
        """Display the main menu."""
        while True:
            self.clear_screen()
            self.stdout.write(f"{BOLD}{BLUE}=== GERENCIADOR DE PERMISSÕES ==={RESET}\n")
            self.stdout.write(f"{BOLD}1.{RESET} Gerenciar grupos")
            self.stdout.write(f"{BOLD}2.{RESET} Gerenciar permissões")
            self.stdout.write(f"{BOLD}3.{RESET} Importar configuração")
            self.stdout.write(f"{BOLD}4.{RESET} Exportar configuração")
            self.stdout.write(f"{BOLD}5.{RESET} Sair\n")

            choice = input("Escolha uma opção: ")

            if choice == "1":
                self.manage_groups_menu()
            elif choice == "2":
                self.manage_permissions_menu()
            elif choice == "3":
                self.import_config()
            elif choice == "4":
                self.export_config()
            elif choice == "5":
                self.stdout.write("Saindo do gerenciador de permissões...")
                break
            else:
                self.stdout.write(f"{YELLOW}Opção inválida. Tente novamente.{RESET}")
                self.wait_for_key()

    def manage_groups_menu(self):
        """Display the groups management menu."""
        while True:
            self.clear_screen()
            self.stdout.write(f"{BOLD}{BLUE}=== GERENCIAR GRUPOS ==={RESET}\n")
            self.stdout.write(f"{BOLD}1.{RESET} Listar grupos")
            self.stdout.write(f"{BOLD}2.{RESET} Criar grupo")
            self.stdout.write(f"{BOLD}3.{RESET} Excluir grupo")
            self.stdout.write(f"{BOLD}4.{RESET} Criar grupos padrão")
            self.stdout.write(f"{BOLD}5.{RESET} Atualizar arquivo de permissões padrão")
            self.stdout.write(f"{BOLD}6.{RESET} Voltar\n")

            choice = input("Escolha uma opção: ")

            if choice == "1":
                self.list_groups()
            elif choice == "2":
                self.create_group()
            elif choice == "3":
                self.delete_group()
            elif choice == "4":
                self.create_default_groups()
            elif choice == "5":
                self.update_default_permissions()
            elif choice == "6":
                break
            else:
                self.stdout.write(f"{YELLOW}Opção inválida. Tente novamente.{RESET}")
                self.wait_for_key()

    def manage_permissions_menu(self):
        """Display the permissions management menu."""
        while True:
            self.clear_screen()
            self.stdout.write(f"{BOLD}{BLUE}=== GERENCIAR PERMISSÕES ==={RESET}\n")
            self.stdout.write(f"{BOLD}1.{RESET} Visualizar permissões de um grupo")
            self.stdout.write(f"{BOLD}2.{RESET} Configurar permissões de um grupo")
            self.stdout.write(f"{BOLD}3.{RESET} Voltar\n")

            choice = input("Escolha uma opção: ")

            if choice == "1":
                self.view_group_permissions()
            elif choice == "2":
                self.configure_group_permissions()
            elif choice == "3":
                break
            else:
                self.stdout.write(f"{YELLOW}Opção inválida. Tente novamente.{RESET}")
                self.wait_for_key()

    def list_groups(self):
        """List all available groups."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== GRUPOS DISPONÍVEIS ==={RESET}\n")

        groups = Group.objects.all().order_by("name")

        if not groups:
            self.stdout.write("Nenhum grupo encontrado.")
        else:
            for i, group in enumerate(groups, 1):
                self.stdout.write(f"{i}. {group.name}")

        self.stdout.write("")
        self.wait_for_key()

    def create_group(self):
        """Create a new group."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== CRIAR GRUPO ==={RESET}\n")

        group_name = input("Nome do grupo (ou deixe em branco para cancelar): ")

        if not group_name:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return

        if Group.objects.filter(name=group_name).exists():
            self.stdout.write(f"{YELLOW}Grupo '{group_name}' já existe.{RESET}")
        else:
            Group.objects.create(name=group_name)
            self.stdout.write(f"{GREEN}Grupo '{group_name}' criado com sucesso.{RESET}")

        self.wait_for_key()

    def delete_group(self):
        """Delete an existing group."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== EXCLUIR GRUPO ==={RESET}\n")

        groups = list(Group.objects.all().order_by("name"))

        if not groups:
            self.stdout.write("Nenhum grupo encontrado.")
            self.wait_for_key()
            return

        for i, group in enumerate(groups, 1):
            self.stdout.write(f"{i}. {group.name}")

        self.stdout.write("")
        choice = input("Número do grupo para excluir (ou deixe em branco para cancelar): ")

        if not choice:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return

        try:
            index = int(choice) - 1
            if 0 <= index < len(groups):
                group_name = groups[index].name
                confirm = input(f"Tem certeza que deseja excluir o grupo '{group_name}'? (s/N): ")

                if confirm.lower() == "s":
                    groups[index].delete()
                    self.stdout.write(f"{GREEN}Grupo '{group_name}' excluído com sucesso.{RESET}")
                else:
                    self.stdout.write("Operação cancelada.")
            else:
                self.stdout.write(f"{YELLOW}Número inválido.{RESET}")
        except ValueError:
            self.stdout.write(f"{YELLOW}Entrada inválida.{RESET}")

        self.wait_for_key()

    def create_default_groups(self):
        """Create the default groups."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== CRIAR GRUPOS PADRÃO ==={RESET}\n")

        created = 0
        existing = 0

        for group_name in DEFAULT_GROUPS:
            if Group.objects.filter(name=group_name).exists():
                self.stdout.write(f"Grupo '{group_name}' já existe.")
                existing += 1
            else:
                Group.objects.create(name=group_name)
                self.stdout.write(f"{GREEN}Grupo '{group_name}' criado com sucesso.{RESET}")
                created += 1

        self.stdout.write(f"\n{created} grupos criados, {existing} já existiam.")
        self.wait_for_key()

    def view_group_permissions(self):
        """Visualiza permissões de um grupo."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== VISUALIZAR PERMISSÕES DE GRUPO ==={RESET}\n")

        group = self.select_group()
        if not group:
            return

        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== PERMISSÕES DO GRUPO: {group.name} ==={RESET}\n")

        current_config = self.permission_manager.export_current_permissions()
        group_config = current_config.get(group.name, {"apps": {}})

        if not group_config["apps"]:
            self.stdout.write("Nenhuma permissão configurada para este grupo.")
        else:
            for app_name, permissions in group_config["apps"].items():
                self.stdout.write(f"\n{BOLD}App: {app_name}{RESET}")
                for operation, enabled in permissions.items():
                    status = f"{GREEN}Sim{RESET}" if enabled else f"{YELLOW}Não{RESET}"
                    self.stdout.write(f"  {operation.capitalize()}: {status}")

        self.stdout.write("")
        self.wait_for_key()

    def configure_group_permissions(self):
        """Configura permissões de um grupo."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== CONFIGURAR PERMISSÕES DE GRUPO ==={RESET}\n")

        group = self.select_group()
        if not group:
            return

        app = self.select_app()
        if not app:
            return

        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== CONFIGURAR PERMISSÕES: {group.name} / {app} ==={RESET}\n")

        current_config = self.permission_manager.export_current_permissions()
        group_config = current_config.get(group.name, {"apps": {}})
        app_config = group_config["apps"].get(app, {"create": False, "read": False, "update": False, "delete": False})

        self.stdout.write(f"{BOLD}Configuração atual:{RESET}")
        for operation, enabled in app_config.items():
            status = f"{GREEN}Sim{RESET}" if enabled else f"{YELLOW}Não{RESET}"
            self.stdout.write(f"  {operation.capitalize()}: {status}")

        self.stdout.write("\n" + "-" * 40 + "\n")

        new_config = {}
        for operation in ["create", "read", "update", "delete"]:
            current = "s" if app_config.get(operation, False) else "n"
            choice = input(f"Permitir {operation.capitalize()}? (s/n) [{current}]: ").lower()

            if not choice:
                choice = current

            new_config[operation] = choice == "s"

        self.stdout.write("\n" + "-" * 40 + "\n")
        self.stdout.write(f"{BOLD}Nova configuração:{RESET}")
        for operation, enabled in new_config.items():
            status = f"{GREEN}Sim{RESET}" if enabled else f"{YELLOW}Não{RESET}"
            self.stdout.write(f"  {operation.capitalize()}: {status}")

        confirm = input("\nConfirmar alterações? (s/N): ").lower()

        if confirm == "s":
            success = self.permission_manager.set_group_permissions(group.name, app, new_config)

            if success:
                if self.permission_manager.json_file:
                    save_success = self.permission_manager.save_config()
                    if save_success:
                        self.stdout.write(
                            f"{GREEN}Permissões atualizadas com sucesso e salvas no arquivo de configuração.{RESET}"
                        )
                        logger.info(
                            f"Permissões atualizadas com sucesso e salvas em {self.permission_manager.json_file}"
                        )
                    else:
                        self.stdout.write(
                            f"{GREEN}Permissões atualizadas com sucesso no banco de dados, mas {YELLOW}falha ao salvar no arquivo de configuração.{RESET}"
                        )
                        logger.error(f"Falha ao salvar configuração no arquivo {self.permission_manager.json_file}")
                else:
                    save_file = input("\nDeseja salvar a configuração em um arquivo JSON? (s/N): ").lower()
                    if save_file == "s":
                        file_path = input("Caminho para salvar o arquivo JSON: ")
                        if file_path:
                            save_success = self.permission_manager.save_config(file_path)
                            if save_success:
                                self.stdout.write(
                                    f"{GREEN}Permissões atualizadas com sucesso e salvas em {file_path}.{RESET}"
                                )
                                logger.info(f"Permissões atualizadas com sucesso e salvas em {file_path}")
                            else:
                                self.stdout.write(
                                    f"{GREEN}Permissões atualizadas com sucesso no banco de dados, mas {YELLOW}falha ao salvar no arquivo.{RESET}"
                                )
                                logger.error(f"Falha ao salvar configuração no arquivo {file_path}")
                        else:
                            self.stdout.write(f"{GREEN}Permissões atualizadas com sucesso no banco de dados.{RESET}")
                            logger.info("Permissões atualizadas com sucesso no banco de dados (sem arquivo)")
                    else:
                        self.stdout.write(f"{GREEN}Permissões atualizadas com sucesso no banco de dados.{RESET}")
                        logger.info("Permissões atualizadas com sucesso no banco de dados (sem arquivo)")

                update_default = input("\nDeseja atualizar o arquivo de permissões padrão? (s/N): ").lower()
                if update_default == "s":
                    try:
                        current_config = self.permission_manager.export_current_permissions()

                        directory = os.path.dirname(settings.DEFAULT_PERMISSIONS_PATH)
                        if directory and not os.path.exists(directory):
                            os.makedirs(directory)

                        with open(settings.DEFAULT_PERMISSIONS_PATH, "w") as f:
                            json.dump(current_config, f, indent=4)

                        self.stdout.write(f"{GREEN}Arquivo de permissões padrão atualizado com sucesso.{RESET}")
                        logger.info(
                            f"Arquivo de permissões padrão atualizado com sucesso: {settings.DEFAULT_PERMISSIONS_PATH}"
                        )
                    except Exception as e:
                        self.stdout.write(f"{YELLOW}Erro ao atualizar arquivo de permissões padrão: {e!s}{RESET}")
                        logger.error(f"Erro ao atualizar arquivo de permissões padrão: {e!s}", exc_info=True)
            else:
                self.stdout.write(f"{YELLOW}Falha ao atualizar permissões.{RESET}")
                logger.error(f"Falha ao atualizar permissões para o grupo {group.name} e app {app}")
        else:
            self.stdout.write("Operação cancelada.")

        self.wait_for_key()

    def import_config(self):
        """Importa configuração de um arquivo JSON."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== IMPORTAR CONFIGURAÇÃO ==={RESET}\n")

        file_path = input("Caminho do arquivo JSON (ou deixe em branco para cancelar): ")

        if not file_path:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return

        if not os.path.exists(file_path):
            self.stdout.write(f"{YELLOW}Arquivo não encontrado: {file_path}{RESET}")
            self.wait_for_key()
            return

        try:
            with open(file_path) as f:
                config = json.load(f)

            for group_name, group_config in config.items():
                for app_name, app_permissions in group_config.get("apps", {}).items():
                    success = self.permission_manager.set_group_permissions(group_name, app_name, app_permissions)

                    status = f"{GREEN}Sucesso{RESET}" if success else f"{YELLOW}Falha{RESET}"
                    self.stdout.write(f"Grupo {group_name}, App {app_name}: {status}")
                    if not success:
                        logger.warning(f"Falha ao configurar permissões para Grupo {group_name}, App {app_name}")

            if self.permission_manager.json_file:
                save_success = self.permission_manager.save_config()
                if save_success:
                    self.stdout.write(f"\n{GREEN}Configuração importada e salva com sucesso.{RESET}")
                    logger.info(f"Configuração importada e salva com sucesso em {self.permission_manager.json_file}")
                else:
                    self.stdout.write(
                        f"\n{GREEN}Configuração importada com sucesso, mas {YELLOW}falha ao salvar no arquivo de configuração.{RESET}"
                    )
                    logger.error(f"Falha ao salvar configuração no arquivo {self.permission_manager.json_file}")
            else:
                self.stdout.write(f"\n{GREEN}Configuração importada com sucesso.{RESET}")
                logger.info("Configuração importada com sucesso (sem arquivo de configuração)")
        except Exception as e:
            self.stdout.write(f"{YELLOW}Erro ao importar configuração: {e!s}{RESET}")
            logger.error(f"Erro ao importar configuração: {e!s}", exc_info=True)

        self.wait_for_key()

    def export_config(self):
        """Exporta configuração para um arquivo JSON."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== EXPORTAR CONFIGURAÇÃO ==={RESET}\n")

        file_path = input("Caminho para salvar o arquivo JSON (ou deixe em branco para cancelar): ")

        if not file_path:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return

        try:
            current_config = self.permission_manager.export_current_permissions()

            directory = os.path.dirname(file_path)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(file_path, "w") as f:
                json.dump(current_config, f, indent=4)

            self.stdout.write(f"{GREEN}Configuração exportada com sucesso para {file_path}{RESET}")
            logger.info(f"Configuração exportada com sucesso para {file_path}")
        except Exception as e:
            self.stdout.write(f"{YELLOW}Erro ao exportar configuração: {e!s}{RESET}")
            logger.error(f"Erro ao exportar configuração: {e!s}", exc_info=True)

        self.wait_for_key()

    def select_group(self):
        """Seleciona um grupo."""
        groups = list(Group.objects.all().order_by("name"))

        if not groups:
            self.stdout.write("Nenhum grupo encontrado.")
            self.wait_for_key()
            return None

        for i, group in enumerate(groups, 1):
            self.stdout.write(f"{i}. {group.name}")

        self.stdout.write("")
        choice = input("Número do grupo (ou deixe em branco para cancelar): ")

        if not choice:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(groups):
                return groups[index]
            else:
                self.stdout.write(f"{YELLOW}Número inválido.{RESET}")
                logger.warning(f"Número de grupo inválido: {choice}")
                self.wait_for_key()
                return None
        except ValueError:
            self.stdout.write(f"{YELLOW}Entrada inválida.{RESET}")
            logger.error(f"Erro ao converter escolha de grupo para número: {choice}")
            self.wait_for_key()
            return None

    def select_app(self):
        """Seleciona um app."""
        app_configs = list(apps.get_app_configs())
        app_names = [app.name for app in app_configs]
        app_names.sort()

        for i, app_name in enumerate(app_names, 1):
            self.stdout.write(f"{i}. {app_name}")

        self.stdout.write("")
        choice = input("Número do app (ou deixe em branco para cancelar): ")

        if not choice:
            self.stdout.write("Operação cancelada.")
            self.wait_for_key()
            return None

        try:
            index = int(choice) - 1
            if 0 <= index < len(app_names):
                return app_names[index]
            else:
                self.stdout.write(f"{YELLOW}Número inválido.{RESET}")
                logger.warning(f"Número de app inválido: {choice}")
                self.wait_for_key()
                return None
        except ValueError:
            self.stdout.write(f"{YELLOW}Entrada inválida.{RESET}")
            logger.error(f"Erro ao converter escolha de app para número: {choice}")
            self.wait_for_key()
            return None

    def clear_screen(self):
        """Limpa a tela do terminal."""
        # Usar print para limpar a tela de forma segura
        logging.debug("\033[2J\033[H")

    def update_default_permissions(self):
        """Atualiza o arquivo de permissões padrão com a configuração atual."""
        self.clear_screen()
        self.stdout.write(f"{BOLD}{BLUE}=== ATUALIZAR ARQUIVO DE PERMISSÕES PADRÃO ==={RESET}\n")

        self.stdout.write(f"Arquivo de permissões padrão: {settings.DEFAULT_PERMISSIONS_PATH}\n")

        if os.path.exists(settings.DEFAULT_PERMISSIONS_PATH):
            self.stdout.write("O arquivo de permissões padrão já existe.")
            confirm = input("Deseja sobrescrever o arquivo existente? (s/N): ").lower()

            if confirm != "s":
                self.stdout.write("Operação cancelada.")
                self.wait_for_key()
                return

        try:
            current_config = self.permission_manager.export_current_permissions()

            directory = os.path.dirname(settings.DEFAULT_PERMISSIONS_PATH)
            if directory and not os.path.exists(directory):
                os.makedirs(directory)

            with open(settings.DEFAULT_PERMISSIONS_PATH, "w") as f:
                json.dump(current_config, f, indent=4)

            self.stdout.write(f"{GREEN}Arquivo de permissões padrão atualizado com sucesso.{RESET}")
            logger.info(f"Arquivo de permissões padrão atualizado com sucesso: {settings.DEFAULT_PERMISSIONS_PATH}")
        except Exception as e:
            self.stdout.write(f"{YELLOW}Erro ao atualizar arquivo de permissões padrão: {e!s}{RESET}")
            logger.error(f"Erro ao atualizar arquivo de permissões padrão: {e!s}", exc_info=True)

        self.wait_for_key()

    def wait_for_key(self):
        """Aguarda o usuário pressionar uma tecla para continuar."""
        input("\nPressione Enter para continuar...")
