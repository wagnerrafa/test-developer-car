"""
Base test classes and utilities for testing framework.

This module provides base classes and utilities for creating and running tests
in the application. It includes classes for handling test output formatting,
common test methods, and test data generation.
"""

import contextlib
import logging
import sys

from colorama import Fore, Style, init
from django.core.management import color_style
from django.core.management.base import OutputWrapper
from faker import Faker
from model_bakery import baker

from drf_base_apps.utils import get_url_from_name
from drf_base_config.settings import API_VERSION, LOGGER_TEST, PRINT_DEBUG, TOKEN_TEST

init()


class BasePrints:
    """
    Base class for handling console output formatting in tests.

    Provides methods to print messages with different colors and styles
    for better test output readability.
    """

    stdout = OutputWrapper(sys.stdout)
    style = color_style()

    def print_start(self, *msgs):
        """Print messages in console with warning style."""
        for msg in msgs:
            self.stdout.write(Fore.YELLOW + str(msg) + Style.RESET_ALL)

    def print_msg(self, *msgs):
        """Print messages in console with info style."""
        for msg in msgs:
            self.stdout.write(Fore.BLUE + str(msg) + Style.RESET_ALL)

    def print_error(self, *msgs):
        """Print messages in console with error style."""
        for msg in msgs:
            self.stdout.write(Fore.RED + str(msg) + Style.RESET_ALL)

    def print_success(self, *msgs):
        """Print messages in console with success style."""
        for msg in msgs:
            self.stdout.write(Fore.GREEN + str(msg) + Style.RESET_ALL)

    def print_notice(self, *msgs):
        """Print messages in console with notice style."""
        for msg in msgs:
            self.stdout.write(Fore.GREEN + str(msg) + Style.RESET_ALL)

    def print_debug(self, *msgs):
        """Print debug messages if debug mode is enabled."""
        if PRINT_DEBUG:
            self.print_notice(msgs)

    def execute_before_and_after(self, func):
        """
        Print start, success or error messages before and after test execution.

        Args:
            func: The function to be decorated.

        Returns:
            The decorated function.

        """

        def wrapper(*args, **kwargs):
            names = str(args[0]).split(".")
            class_name = names[-2].replace(")", "") if names[0].strip().endswith("apps") else names[-1].replace(")", "")

            class_name = class_name.split("object at")[0].strip()

            method = func.__name__

            # Tentar obter o nome do método de teste atual
            import inspect

            current_frame = inspect.currentframe()
            test_method_name = "unknown"
            last_valid_method = "unknown"

            # Procurar pelo método de teste na pilha de chamadas
            # Pular os métodos internos como test_api_a_post, test_api_b_get, etc.
            while current_frame:
                frame_info = inspect.getframeinfo(current_frame)
                if frame_info.function.startswith("test_") and not frame_info.function.startswith("test_api_"):
                    test_method_name = frame_info.function
                    break
                elif frame_info.function.startswith("test_"):
                    last_valid_method = frame_info.function
                current_frame = current_frame.f_back

            # Se não encontrou um método específico, usar o último válido
            if test_method_name == "unknown" and last_valid_method != "unknown":
                test_method_name = last_valid_method

            http_method = (
                "GET"
                if "get" in method.lower()
                else (
                    "POST"
                    if "post" in method.lower()
                    else "PUT" if "put" in method.lower() else "DELETE" if "delete" in method.lower() else "UNKNOWN"
                )
            )
            try:
                # Determinar o método HTTP baseado no nome da função

                self.print_start(f"Executando {http_method} {class_name}.{test_method_name}")
                resultado = func(*args, **kwargs)
                if resultado:
                    if resultado["success"]:
                        self.print_success(f"Executado {http_method} {class_name}.{test_method_name} com sucesso\n")
                    else:
                        self.print_error(f"Executado {http_method} {class_name}.{test_method_name} sem sucesso\n")
                        self.print_error(resultado, "\n")

                    if PRINT_DEBUG:
                        logging.debug(resultado)
                    return resultado
                self.print_start(f"Sem testes para {http_method} {class_name}.{test_method_name}\n")
            except AssertionError as e:
                self.print_error(f"Executado {http_method} {class_name}.{test_method_name} sem sucesso\n")
                raise e
            return

        return wrapper


execute_before_and_after = BasePrints().execute_before_and_after


class BaseTests(BasePrints):
    """
    Base class for tests with common methods and attributes.

    Attributes:
        faker: An instance of Faker used to generate fake data.
        base_path: Base API version path.
        status_expected: Expected HTTP status codes for different methods.
        http_method_names: List of supported HTTP methods.
        token: Test authentication token.
        logger: Test logger instance.
        path_parameters: Dictionary of path parameters.

    Methods:
        execute_before_and_after: Decorator for test execution logging.
        fake_model_data: Create fake model instances using Baker.
        return_response: Format and return test response data.
        format_url: Format URL for API endpoint testing.
        has_post: Check if POST method is supported.
        has_get: Check if GET method is supported.
        has_put: Check if PUT method is supported.
        get_path: Get test execution path.
        get_path_post: Get POST test execution path.
        get_parameters: Get test parameters.
        generate_name: Generate fake name using Faker.
        get_headers: Get HTTP headers for requests.

    """

    faker = Faker("pt_BR")
    base_path = API_VERSION

    status_expected = {"GET": 200, "POST": 201, "PUT": 200}
    http_method_names = ["get", "post"]

    token = TOKEN_TEST
    logger = LOGGER_TEST
    path_parameters = {}

    @staticmethod
    def execute_before_and_after(func):
        """Return the execute_before_and_after decorator."""
        return execute_before_and_after(func)

    @staticmethod
    def fake_model_data(model, quantity=1, **attrs):
        """
        Create fake model instances using Baker.

        Args:
            model: The Django model to create instances for.
            quantity: Number of instances to create.
            **attrs: Specific attributes to override generated values.

        Returns:
            One or more model instances.

        """
        return baker.make(model, _quantity=quantity, **attrs)

    def return_response(self, data, response):
        """
        Format and return test response data.

        Args:
            data: Response data dictionary.
            response: HTTP response object.

        Returns:
            Formatted response data as AttrDict.

        """
        data["status_code"] = response.status_code
        data["content"] = response.content
        with contextlib.suppress(ValueError):
            data["content"] = response.json()
        data["success"] = str(response.status_code).startswith("2")
        return self.AttrDict(data)

    def format_url(self, path: str, params=None) -> str:
        """
        Format and return URL for API endpoint testing.

        Args:
            path: API endpoint path.
            params: URL parameters.

        Returns:
            Formatted URL string.

        """
        params = params if params is not None else self.path_parameters
        return get_url_from_name(path, params)

    def has_post(self):
        """
        Check if POST method is in available HTTP methods.

        Returns:
            True if 'post' is in the list, False otherwise.

        """
        return "post" in self.http_method_names

    def has_get(self):
        """
        Check if GET method is in available HTTP methods.

        Returns:
            True if 'get' is in the list, False otherwise.

        """
        return "get" in self.http_method_names

    def has_put(self):
        """
        Check if PUT method is in available HTTP methods.

        Returns:
            True if 'put' is in the list, False otherwise.

        """
        return "put" in self.http_method_names

    def get_path(self):
        """Return path for test execution, adding trailing slash if missing."""
        path = getattr(self, "path_get", None) or getattr(self, "path", None)
        return path

    def get_path_post(self):
        """Return path for POST test execution, adding trailing slash if missing."""
        path = getattr(self, "path", None)
        if path and self.has_post() and str(path).endswith("/") is False:
            path = str(path) + "/"
        return path

    def get_parameters(self) -> dict or None:
        """Return test parameters for execution."""
        if hasattr(self, "parameters"):
            if callable(self.parameters):
                return self.parameters()
            return self.parameters

    class AttrDict(dict):
        """
        Dictionary subclass that allows attribute access to content.

        Methods:
            __getattr__: Return attribute value or raise AttributeError.
            __setattr__: Set attribute value.

        """

        def __getattr__(self, attr):
            """Return attribute value or raise AttributeError if not found."""
            return self[attr]

        def __setattr__(self, attr, value):
            """Set attribute value."""
            self[attr] = value

    def generate_name(self):
        """Generate fake name using Faker library."""
        return self.faker.name()

    def get_headers(self) -> dict:
        """Return HTTP headers for API requests."""
        return {"Authorization": f"Token {self.token}", "Content-type": "application/json"}
