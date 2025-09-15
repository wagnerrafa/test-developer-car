"""
Group-based permissions management system.

This module provides a comprehensive system for managing group-based permissions
using JSON configuration files and database synchronization.
"""

import json
import logging
import os

from django.apps import apps
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

logger = logging.getLogger(__name__)


class GroupPermissionManager:
    """Manager for group-based permissions using JSON configuration."""

    def __init__(self, json_file=None):
        """Initialize the permission manager with optional JSON file."""
        self.json_file = json_file
        self.permissions_config = self._load_config()

    def _load_config(self):
        """Load permissions configuration from JSON file or use default configuration."""
        if self.json_file and os.path.exists(self.json_file):
            with open(self.json_file) as f:
                return json.load(f)
        return {}

    def save_config(self, file_path=None):
        """Save current configuration to a JSON file."""
        save_path = file_path or self.json_file
        if save_path:
            try:
                logger.info(f"Tentando salvar configuração em {save_path}")
                directory = os.path.dirname(save_path)
                if directory and not os.path.exists(directory):
                    os.makedirs(directory)
                    logger.info(f"Diretório criado: {directory}")

                with open(save_path, "w") as f:
                    json.dump(self.permissions_config, f, indent=4)

                logger.info(f"Configuração salva com sucesso em {save_path}")
                logger.info(f"Conteúdo da configuração: {self.permissions_config}")
                return True
            except Exception as e:
                logger.error(f"Erro ao salvar configuração em {save_path}: {e!s}", exc_info=True)
                return False
        else:
            logger.warning("Nenhum caminho de arquivo fornecido para salvar a configuração")
            return False

    def get_group_permissions(self, group_name):
        """Return permissions configuration for a specific group."""
        return self.permissions_config.get(group_name, {})

    def set_group_permissions(self, group_name, app_name, crud_permissions):
        """
        Set CRUD permissions for a specific app in a group.

        Args:
            group_name (str): Group name
            app_name (str): App name
            crud_permissions (dict): Dictionary with CRUD permissions (create, read, update, delete)

        """
        if group_name not in self.permissions_config:
            self.permissions_config[group_name] = {"apps": {}}

        if "apps" not in self.permissions_config[group_name]:
            self.permissions_config[group_name]["apps"] = {}

        self.permissions_config[group_name]["apps"][app_name] = crud_permissions

        self._update_db_permissions(group_name, app_name, crud_permissions)

        return True

    def _update_db_permissions(self, group_name, app_name, crud_permissions):
        """Update permissions in the database for a specific group and app."""
        from django.db import transaction

        try:
            group = Group.objects.get(name=group_name)
            logger.info(f"Atualizando permissões para o grupo '{group_name}' no app '{app_name}'")

            # Cria mapeamento bidirecional entre app_label e app_name
            app_label_to_name = {}
            name_to_app_label = {}
            app_name_parts = {}  # Para mapear nomes de apps com caminhos completos

            for app_config in apps.get_app_configs():
                app_label_to_name[app_config.label] = app_config.name
                name_to_app_label[app_config.name] = app_config.label

                # Adiciona mapeamento para partes do nome do app
                parts = app_config.name.split(".")
                if len(parts) > 1:
                    app_name_parts[app_config.name] = app_config.label
                    app_name_parts[parts[-1]] = app_config.label

            logger.info(f"Mapeamento de app_name para app_label: {name_to_app_label}")
            logger.info(f"Mapeamento de partes de app_name: {app_name_parts}")

            if app_name in name_to_app_label:
                app_label = name_to_app_label[app_name]
            elif app_name in app_name_parts:
                # Correspondência com parte do nome do app
                app_label = app_name_parts[app_name]
            elif app_name in app_label_to_name:
                # O app_name já é um app_label
                app_label = app_name
            else:
                app_label = app_name.split(".")[-1] if "." in app_name else app_name

            logger.info(f"Usando app_label '{app_label}' para o app '{app_name}'")

            try:
                app_models = list(apps.get_app_config(app_label).get_models())
                logger.info(f"Encontrados {len(app_models)} modelos no app '{app_label}'")
            except LookupError as e:
                logger.error(f"Erro ao buscar modelos do app '{app_label}': {e!s}", exc_info=True)
                error_msg = str(e)
                if "Did you mean" in error_msg:
                    import re

                    suggested_app = re.search(r"Did you mean '([^']+)'", error_msg)
                    if suggested_app:
                        suggested_app_label = suggested_app.group(1)
                        logger.info(f"Tentando usar app_label sugerido: '{suggested_app_label}'")
                        try:
                            app_models = list(apps.get_app_config(suggested_app_label).get_models())
                            logger.info(f"Encontrados {len(app_models)} modelos no app '{suggested_app_label}'")
                            app_label = suggested_app_label
                        except Exception as inner_e:
                            logger.error(f"Erro ao usar app_label sugerido: {inner_e!s}", exc_info=True)
                            return False
                    else:
                        return False
                else:
                    return False

            with transaction.atomic():
                for model in app_models:
                    model_name = model._meta.model_name
                    content_type = ContentType.objects.get_for_model(model)
                    logger.info(f"Processando modelo '{model_name}' (content_type_id={content_type.id})")

                    crud_map = {
                        "create": f"add_{model_name}",
                        "read": f"view_{model_name}",
                        "update": f"change_{model_name}",
                        "delete": f"delete_{model_name}",
                    }

                    for perm_name in crud_map.values():
                        try:
                            perm = Permission.objects.get(codename=perm_name, content_type=content_type)
                            if perm in group.permissions.all():
                                logger.info(f"Removendo permissão '{perm_name}' do grupo '{group_name}'")
                                group.permissions.remove(perm)
                        except Permission.DoesNotExist:
                            logger.warning(f"Permissão '{perm_name}' não encontrada para o modelo '{model_name}'")

                    for crud_op, perm_name in crud_map.items():
                        if crud_permissions.get(crud_op, False):
                            try:
                                perm = Permission.objects.get(codename=perm_name, content_type=content_type)
                                logger.info(f"Adicionando permissão '{perm_name}' ao grupo '{group_name}'")
                                group.permissions.add(perm)

                                group.refresh_from_db()
                                if perm not in group.permissions.all():
                                    logger.error(f"Falha ao adicionar permissão '{perm_name}' ao grupo '{group_name}'")
                                    raise Exception(
                                        f"Falha ao adicionar permissão '{perm_name}' ao grupo '{group_name}'"
                                    )
                            except Permission.DoesNotExist:
                                logger.warning(f"Permissão '{perm_name}' não encontrada para o modelo '{model_name}'")

                group.save()
                logger.info(f"Permissões atualizadas com sucesso para o grupo '{group_name}' no app '{app_name}'")

            return True
        except Group.DoesNotExist:
            logger.error(f"Grupo '{group_name}' não encontrado", exc_info=True)
            return False
        except Exception as e:
            logger.error(
                f"Erro ao atualizar permissões para o grupo '{group_name}' no app '{app_name}': {e!s}", exc_info=True
            )
            return False

    def export_current_permissions(self):
        """Export current permissions configuration from the database."""
        current_config = {}

        # Cria mapeamento bidirecional entre app_label e app_name
        app_label_to_name = {}
        name_to_app_label = {}
        app_name_parts = {}  # Para mapear partes de nomes de apps

        for app_config in apps.get_app_configs():
            app_label_to_name[app_config.label] = app_config.name
            name_to_app_label[app_config.name] = app_config.label

            # Adiciona mapeamento para partes do nome do app
            parts = app_config.name.split(".")
            if len(parts) > 1:
                app_name_parts[app_config.name] = app_config.label
                app_name_parts[parts[-1]] = app_config.label

        # Cria mapeamento reverso de app_label para nome completo do app
        app_label_to_full_name = {}
        for app_name, app_label in name_to_app_label.items():
            app_label_to_full_name[app_label] = app_name

        logger.info(f"Mapeamento de app_label para app_name: {app_label_to_name}")
        logger.info(f"Mapeamento de app_name para app_label: {name_to_app_label}")
        logger.info(f"Mapeamento de app_label para nome completo: {app_label_to_full_name}")
        logger.info(f"Mapeamento de partes de app_name: {app_name_parts}")

        for group in Group.objects.all():
            group_name = group.name
            group_config = {"apps": {}}

            app_permissions = {}

            # Agrupa permissões por app_label
            app_label_permissions = {}
            for perm in group.permissions.all():
                app_label = perm.content_type.app_label

                if app_label not in app_label_permissions:
                    app_label_permissions[app_label] = []

                app_label_permissions[app_label].append(perm)

            # Processa permissões por app_label
            for app_label, perms in app_label_permissions.items():
                # Tenta obter o nome completo do app para este app_label
                app_display_name = app_label_to_full_name.get(app_label, app_label)

                logger.info(
                    f"Processando permissões para app_label '{app_label}', usando nome de exibição '{app_display_name}'"
                )

                if app_display_name not in app_permissions:
                    app_permissions[app_display_name] = {
                        "create": False,
                        "read": False,
                        "update": False,
                        "delete": False,
                    }

                for perm in perms:
                    if perm.codename.startswith("add_"):
                        app_permissions[app_display_name]["create"] = True
                    elif perm.codename.startswith("view_"):
                        app_permissions[app_display_name]["read"] = True
                    elif perm.codename.startswith("change_"):
                        app_permissions[app_display_name]["update"] = True
                    elif perm.codename.startswith("delete_"):
                        app_permissions[app_display_name]["delete"] = True

            group_config["apps"] = app_permissions
            current_config[group_name] = group_config

        self.permissions_config = current_config
        return current_config
