"""
Management command to generate test scripts from API schema.

This module provides a Django management command that generates test scripts
automatically from the API schema documentation.
"""

import logging
import os
import re

from django.apps import apps
from django.core.management import BaseCommand
from django.db.models.fields.related_descriptors import ForwardManyToOneDescriptor
from django.urls import resolve
from django.urls.exceptions import Resolver404

from drf_base_config.schema_generator import CustomSchemaGenerator
from drf_base_config.settings import STATIC_DIR

METHODS = {"post": 201, "get": 200, "put": 200, "patch": 200, "delete": 200}


class TestScriptGenerator:
    """Generate test scripts from API schema."""

    exclude_apps = (
        ("big_number", "v1"),
        ("calculation", "funds_payment_detail_v1"),
        ("calculation", "funds_payment_due_detail_v1"),
        ("calculation", "funds_payment"),
    )

    def __init__(self, schema):
        """Initialize the test script generator with schema."""
        self.schema = schema

    def generate_scripts(self):
        """Generate test scripts for all API endpoints."""
        for path, methods in self.schema["paths"].items():
            for method, details in methods.items():
                self.generate_script(path, method, details)

    def generate_script(self, path, method, details):
        """Generate a test script for a specific API endpoint."""
        url_resolve = self.generate_resolve_url(path)

        if not url_resolve:
            logging.debug(f"Could not resolve url: {path}")
            return

        view = url_resolve.func.view_class

        if method.lower() not in [method.lower() for method in view.http_method_names]:
            return

        model = getattr(view, "model", None)

        if not model:
            logging.debug(f"Could not resolve model: {model} view: {view} path: {path}")
            return
        url_name = url_resolve.url_name
        app_name = self.get_app_name(path)
        class_name = self.get_class_name(path, method)
        parameters = details.get("parameters", [])
        request_body = details.get("requestBody", {}).get("content", {}).get("application/json", {}).get("example", {})

        status_expected = {method: METHODS[str(method).lower()]}
        parameters_method = self.generate_parameters_method(model, parameters, request_body)

        path_parameters_method = self.generate_path_parameters_method(model, parameters, path, app_name)

        script_content = f"""
from core.abstract.tests import AbstractTest
from django.test.utils import tag

@tag('integration', 'success')
class {class_name}(AbstractTest):
    path = '{url_name}'
    http_method_names = ['{method}']
    status_expected = {status_expected}

    {parameters_method}
    {path_parameters_method}"""

        self.save_script(path, app_name, method, script_content)

    def generate_parameters_method(self, current_model, parameters, request_body):
        """
        Generate parameters method for test script.

        Args:
            current_model: The model to generate parameters for.
            parameters: List of parameters from API schema.
            request_body: Request body from API schema.

        Returns:
            str: Generated parameters method code.

        """
        if not parameters and not request_body:
            return f"""
    def parameters(self):
        from {current_model.__module__} import {current_model.__name__}
        faker_data = self.create_fake_model_data({current_model.__name__}, first=False)[0]
        return {{}}"""

        list_imports = {}
        list_def_imports = []

        def generate_def_get_id(val):
            if isinstance(val, str) and val.startswith("model_name:"):
                app_name, model_name = val.replace("model_name:", "").split(".")
                model_class = apps.get_model(app_name, model_name)
                model_path = model_class.__module__
                list_imports[
                    model_name
                ] = f"""
    def get_{model_name.lower()}_id(self):
        from {model_path} import {model_name}
        faker_data = self.create_fake_model_data({model_name}, first=False)[0]
        return faker_data.id
"""

                new_method = f"""self.get_{model_name.lower()}_id()"""
                list_def_imports.append(new_method)
                return new_method
            return val

        def replace_ids(data):
            if isinstance(data, dict):
                return {k: generate_def_get_id(v) if isinstance(v, str) else replace_ids(v) for k, v in data.items()}
            elif isinstance(data, list):
                return [generate_def_get_id(item) if isinstance(item, str) else replace_ids(item) for item in data]
            return data

        request_body = replace_ids(request_body)

        for new_def in list_def_imports:
            request_body = str(request_body).replace(f"'{new_def}'", new_def).replace(f'"{new_def}"', new_def)
        list_functions = ""
        list_imports[
            "parameters"
        ] = f"""
    def parameters(self):
        return {request_body!s}"""

        for value in list_imports.values():
            list_functions += value
        return list_functions.strip()

    def generate_resolve_url(self, original_url):
        """
        Generate resolved URL by replacing path parameters with dummy values.

        Args:
            original_url: The original URL with path parameters.

        Returns:
            ResolverMatch: Resolved URL match or None if not found.

        """
        uuid_match = "123e4567-e89b-12d3-a456-426614174000"
        str_match = "dummy"
        id_match = "1"

        matches = (uuid_match, str_match, str_match, id_match)

        for dummy_value in matches:
            original_url = re.sub(r"\{[^}]+\}", dummy_value, original_url)

            try:
                return resolve(original_url)
            except Resolver404:
                continue

    def get_nested_attr(self, attr, model):
        """
        Get nested attribute from model.

        Args:
            attr: Attribute name, can contain '__' for nested access.
            model: The model to get attribute from.

        Returns:
            The attribute value or None if not found.

        """
        new_model = model
        if "__" in attr:
            attr = attr.split("__")
            for a in attr:
                new_model = getattr(new_model, a)
                if isinstance(new_model, ForwardManyToOneDescriptor):
                    new_model = new_model.field.related_model
            return new_model
        return getattr(model, attr, None)

    def generate_path_parameters_method(self, model, parameters, path, app_name):
        """
        Generate path parameters method for test script.

        Args:
            model: The model to generate path parameters for.
            parameters: List of parameters from API schema.
            path: API path.
            app_name: Application name.

        Returns:
            str: Generated path parameters method code.

        """
        path_params = {}

        params = {}
        list_params = []
        if model and parameters:
            for param in parameters:
                if param["in"] == "path":
                    field_name = param["name"]
                    attr = self.get_nested_attr(field_name, model)
                    if attr:
                        params[
                            field_name
                        ] = f"""
    def get_parameter_{field_name.lower()}(self):
        from {model.__module__} import {model.__name__}
        faker_data = self.create_fake_model_data({model.__name__}, first=False)[0]
        return faker_data.{field_name.replace('__', '.')}"""
                        def_name = f"self.get_parameter_{field_name.lower()}()"
                        path_params[field_name] = def_name
                        list_params.append(def_name)
                    else:
                        logging.debug(
                            f"erro em pegar o field: {field_name} na model: {model} e no schema: {path, app_name}\n\n"
                        )
        if not path_params:
            return ""

        for param in list_params:
            path_params = str(path_params).replace(f"'{param}'", param).replace(f'"{param}"', param)

        params_str = "\n".join(params.values())
        return f"""
    {params_str}

    def path_parameters(self):\n        return {path_params}"""

    def get_app_name(self, path):
        """
        Extract application name from API path.

        Args:
            path: API path.

        Returns:
            str: Application name.

        """
        return re.sub(r"/juca/api/v\d+/", "", path.replace("{", "").replace("}", "")).split("/")[0]

    def get_class_name(self, path, method):
        """
        Generate class name for test from path and method.

        Args:
            path: API path.
            method: HTTP method.

        Returns:
            str: Generated class name.

        """
        path_parts = path.replace("{", "").replace("}", "").replace("-", "").strip("/").split("/")
        class_name = "".join(part.capitalize() for part in path_parts)
        return f"{class_name}{method.capitalize()}Test"

    def get_sub_app_name(self, path):
        """
        Extract sub-application name from API path.

        Args:
            path: API path.

        Returns:
            str: Sub-application name with version.

        """
        try:
            version = re.search(r"/juca/api/v\d+/", path).group(0)
        except AttributeError:
            version = "v1"

        path_clean = path.replace("/juca/api/", "").split("{")[0].split("/")[2:]
        path_part = "_".join(path_clean)
        version_clean = version.replace("/juca/api/", "").replace("/", "")
        return f"{path_part}{version_clean}"

    def save_script(self, path, app_name, method, script_content):
        """
        Save generated test script to file.

        Args:
            path: API path.
            app_name: Application name.
            method: HTTP method.
            script_content: Generated script content.

        """
        new_class_name = self.get_sub_app_name(path)
        separated_files = False
        for exclude_app in self.exclude_apps:
            if exclude_app[0] == app_name and exclude_app[1] == new_class_name:
                return

        gen_dir = os.path.join(STATIC_DIR, "generated_tests")
        os.makedirs(gen_dir, exist_ok=True)

        if separated_files:

            gen_dir_path = f"{gen_dir}/{app_name}/{new_class_name}"
            os.makedirs(gen_dir_path, exist_ok=True)
            with open(f"{gen_dir}/{app_name}/{new_class_name}/test_{new_class_name.lower()}_{method}.py", "w") as file:
                file.write(script_content)

        else:
            gen_dir_path = f"{gen_dir}"

            os.makedirs(f"{gen_dir}", exist_ok=True)
            with open(f"{gen_dir}/test_{app_name}_{new_class_name.lower()}_{method}.py", "w") as file:
                file.write(script_content)

        logging.debug(f"Teste gerado no diretório: {gen_dir_path}")


class Command(BaseCommand):
    """Management command to generate test scripts from API schema."""

    def generate_swagger(self):
        """Generate Swagger schema for test generation."""
        generator = CustomSchemaGenerator()
        return generator.get_schema()

    def handle(self, *args, **options):
        """Handle the command execution."""
        schema = self.generate_swagger()
        generator = TestScriptGenerator(schema)
        generator.generate_scripts()
