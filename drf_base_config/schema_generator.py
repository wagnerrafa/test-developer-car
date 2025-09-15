"""
rest_framework.schemas.

schemas:
    __init__.py
    generators.py   # Top-down schema generation
    inspectors.py   # Per-endpoint view introspection
    utils.py        # Shared helper functions
    views.py        # Houses `SchemaView`, `APIView` subclass.

We expose a minimal "public" API directly from `schemas`. This covers the
basic use-cases:

    from rest_framework.schemas import (
        AutoSchema,
        ManualSchema,
        get_schema_view,
        SchemaGenerator,
    )

Other access should target the submodules directly
"""

import os
from urllib.parse import urljoin

from django import apps
from rest_framework.schemas.openapi import SchemaGenerator

from drf_base_config import settings


class CustomSchemaGenerator(SchemaGenerator):
    """Gerador de schema personalizado para OpenAPI."""

    format_string_examples = {
        "date-time": "2020-07-01T12:29:56.203Z",
        "uuid": "3fa85f64-5717-4562-b3fc-2c962f66afa7",
        "email": "example@example.com",
        "uri": "http://example.com",
        "binary": "base64_encoded_binary_data",
    }

    def __init__(self, save_swagger=False, *args, **kwargs):
        """Inicializa o gerador de schema personalizado."""
        self.save_swagger = save_swagger
        self.static_root = getattr(settings, "STATIC_ROOT", None)
        self.static_dir = getattr(settings, "STATIC_DIR", None)
        self.swagger_path = f"{self.static_root}/swagger.json"
        self.base_path = getattr(settings, "API_BASE_PATH", "/")  # Usando a configuração do settings
        super().__init__(*args, **kwargs)

    def get_schema(self, request=None, public=False):
        """Gera o schema OpenAPI completo."""
        self._initialise_endpoints()
        components_schemas = {}

        paths = {}
        _, view_endpoints = self._get_paths_and_endpoints(None if public else request)
        disable_try_it_out_urls = []

        for path, method, view in view_endpoints:
            if view.request:
                headers = dict(view.request.headers)
                headers["X-Swagger-Original-Path"] = path
                view.request.headers = headers
            if not self.has_view_permissions(path, method, view):
                continue

            operation = view.schema.get_operation(path, method)
            components = view.schema.get_components(path, method)
            components_schemas.update(components)

            if self.save_swagger:
                for component_name, component_schema in components.items():
                    model_name = component_schema.get("model_name")
                    example = self.generate_example(component_schema, method, component_name, model_name)
                    if (
                        method in ["POST", "PUT"]
                        and operation["requestBody"]["content"].get("application/json")
                        and example != {}
                    ):
                        operation["requestBody"]["content"]["application/json"]["example"] = example
                    components_schemas.setdefault("schemas", {}).update({component_name: component_schema})

            if path.startswith("/"):
                path = path[1:]

            # Adicionando o subpath base à URL
            path = urljoin(self.base_path, path)
            custom_path = getattr(view, "custom_path", None)
            if custom_path:
                path = custom_path
            paths.setdefault(path, {})
            paths[path][method.lower()] = operation
            try_it_out = getattr(view, "try_it_out", True)
            if not try_it_out:
                disable_try_it_out_urls.append(path)

        self.check_duplicate_operation_id(paths)

        schema = {
            "openapi": "3.0.2",
            "info": self.get_info(),
            "paths": paths,
            "disable_try_it_out_urls": disable_try_it_out_urls,
        }

        if len(components_schemas) > 0:
            schema["components"] = {"schemas": components_schemas}

        if self.save_swagger:
            self.save_json(schema)
        return schema

    def save_json(self, schema):
        """Salva o schema JSON em arquivo."""
        import json

        os.makedirs(self.static_root, exist_ok=True)
        os.makedirs(self.static_dir, exist_ok=True)
        swagger_path = f"{self.static_dir}/swagger.json"
        os.makedirs(self.static_dir, exist_ok=True)
        with open(self.swagger_path, "w") as f:
            f.write(json.dumps(schema, default=str, indent=4))
        with open(swagger_path, "w") as f:
            f.write(json.dumps(schema, default=str, indent=4))

    def generate_example(self, component_schema, method, component_name, model_name):
        """Gera exemplos para o schema do componente."""
        example = {}
        method = method.upper()

        if "properties" not in component_schema:
            return example

        for prop, prop_details in component_schema["properties"].items():
            if method in ["POST", "PUT"] and prop_details.get("readOnly"):
                continue
            if method in ["GET", "DELETE"] and prop_details.get("writeOnly"):
                continue

            example[prop] = self.get_example_field(
                prop, prop_details, method, component_name, component_schema, model_name
            )
        return example

    def snake_to_camel(self, snake_str):
        """
        Convert a string from snake_case format to CamelCase.

        Ex.: "creditor_uuid" → "CreditorUuid".
        """
        return "".join(word.capitalize() for word in snake_str.split("_"))

    def get_example_field(self, prop, prop_details, method, component_name, component_schema, model_name):
        """Gera exemplo para um campo específico."""
        if "type" not in prop_details:
            return prop_details

        def handle_string():
            if "enum" in prop_details:
                return prop_details["enum"][0]
            fmt = prop_details.get("format")

            def handle_datetime():
                return "2020-07-01T12:29:56.203Z"

            def handle_date():
                return "2020-07-01"

            def handle_uuid():
                example_uuid = self.get_uuid_example(
                    prop, prop_details, method, component_name, component_schema, model_name
                )
                if example_uuid:
                    return example_uuid
                return self.format_string_examples.get("uuid", "string")

            def handle_email():
                return self.format_string_examples.get("email", "example@example.com")

            def handle_uri():
                return self.format_string_examples.get("uri", "http://example.com")

            def handle_binary():
                return self.format_string_examples.get("binary", "base64_encoded_binary_data")

            format_dispatch = {
                "date-time": handle_datetime,
                "date": handle_date,
                "uuid": handle_uuid,
                "email": handle_email,
                "uri": handle_uri,
                "binary": handle_binary,
            }
            if fmt in format_dispatch:
                return format_dispatch[fmt]()
            return self.format_string_examples.get(fmt, "string")

        def handle_integer():
            return 1

        def handle_number():
            return 0.0

        def handle_boolean():
            return True

        def handle_object():
            return self.generate_example(prop_details, method, component_name, model_name)

        def handle_array():
            def handle_items():
                return self.generate_example(
                    {"properties": {"items": prop_details["items"]}}, method, component_name, model_name
                ).get("items")

            # Se quiser tratar diferentes formatos de array, pode adicionar aqui
            return [handle_items()]

        def handle_null():
            return None

        type_dispatch = {
            "string": handle_string,
            "integer": handle_integer,
            "number": handle_number,
            "boolean": handle_boolean,
            "object": handle_object,
            "array": handle_array,
            "null": handle_null,
        }

        handler = type_dispatch.get(prop_details["type"], lambda: "value")
        return handler()

    def get_uuid_example(self, prop, prop_details, method, component_name, component_schema, default_model_name):
        """Gera exemplo de UUID baseado no nome da propriedade."""
        base_name = prop
        for suffix in ["_id", "_uuid"]:
            if base_name.endswith(suffix):
                base_name = base_name[: -len(suffix)]
                break

        if "model_name" in prop_details:
            model_name = prop_details["model_name"]
        elif base_name.lower() == "id":
            model_name = default_model_name
        else:
            model_name = self.snake_to_camel(base_name)

        if not model_name:
            return

        model_class = None
        app_name = None
        for app_config in apps.apps.get_app_configs():
            try:
                model_class = app_config.get_model(model_name)
                if model_class:
                    app_name = app_config.label
                    break
            except LookupError:
                continue

        if model_class:
            return f"model_name:{app_name}.{model_name}"
        return None
