"""
Base Django test classes for API testing framework.

This module provides base classes for Django API testing that inherit from
TransactionTestCase. It includes methods for testing HTTP POST and GET requests,
user creation, and response handling. The classes provide helper methods for
printing test results and formatting data for display.
"""

import contextlib
import json
import secrets
import sys
import uuid

from django.contrib.auth.models import Group
from django.contrib.auth.password_validation import validate_password
from django.test import TestCase

from drf_base_apps.core.abstract.base_tests import BaseTests
from drf_base_apps.utils import get_user_model
from drf_base_config.settings import BASE_API_URL

User = get_user_model()

show_result = False


def gerar_cpf():
    """
    Generate a valid Brazilian CPF number.

    Returns:
        str: A formatted CPF string (XXX.XXX.XXX-XX).

    """
    # Gera os 9 primeiros dígitos
    numeros = [secrets.randbelow(10) for _ in range(9)]

    # Calcula o primeiro dígito verificador
    soma = sum((10 - i) * num for i, num in enumerate(numeros))
    primeiro_digito = (11 - soma % 11) if soma % 11 >= 2 else 0
    numeros.append(primeiro_digito)

    # Calcula o segundo dígito verificador
    soma = sum((11 - i) * num for i, num in enumerate(numeros))
    segundo_digito = (11 - soma % 11) if soma % 11 >= 2 else 0
    numeros.append(segundo_digito)

    # Retorna o CPF formatado
    return "{}{}{}.{}{}{}.{}{}{}-{}{}".format(*numeros)


class AbstractTestMeta(type):
    """Metaclass para definir __test__ = False automaticamente em classes abstratas."""

    def __new__(mcs, name, bases, namespace):
        """Set new class configure include in test case."""
        namespace["__test__"] = not str(name).lower().startswith(("abstract", "basetestsdjango", "baseabstracttest"))
        return super().__new__(mcs, name, bases, namespace)


class BaseTestsDjango(BaseTests, TestCase, metaclass=AbstractTestMeta):
    """
    Base test class for Django API testing.

    Inherits from BaseTests and TransactionTestCase to provide comprehensive
    API testing capabilities with database transaction support.

    Attributes:
        base_url: Base URL for API testing.
        path: API endpoint path for testing.
        user: Test user instance.
        username: Username for test user creation.
        set_user: Flag to enable user creation.
        is_superuser: Flag to create superuser.
        is_staff: Flag to create staff user.
        is_active: Flag to create active user.
        group_names: List of group names for user assignment.

    Methods:
        get_base_url: Return base URL for testing.
        def_post: Send HTTP POST request to API endpoint.
        def_post_file: Send HTTP POST request with file upload to API endpoint.
        post: Send HTTP POST request with logging.
        post_file: Send HTTP POST request with file upload and logging.
        get: Send HTTP GET request with logging.
        put: Send HTTP PUT request with logging.
        response: Process and format response data.
        assert_values: Assert response status codes.
        get_path: Get test execution path.
        test_api_a_post: Test POST API endpoint.
        test_api_b_get: Test GET API endpoint.
        create_user: Create test user with specified attributes.
        setUp: Setup test environment and create test user.

    """

    base_url = BASE_API_URL
    path = None
    user = None
    username = "default"
    set_user = True
    is_superuser = False
    is_staff = False
    is_active = True
    group_names = []
    _fake_password = None

    def get_base_url(self):
        """Return base URL for API testing."""
        return self.base_url

    def __init__(self, *args, **kwargs):
        """Initialize test class with keep_db flag based on command line arguments."""
        super().__init__(*args, **kwargs)
        self.keep_db = "--keepdb" in sys.argv

    def def_post(self, path, obj, formatted_url=None, expected=None):
        """
        Send HTTP POST request to API endpoint.

        Args:
            path: API endpoint path.
            obj: Request payload data.
            formatted_url: Pre-formatted URL (optional).
            expected: Expected status code (optional).

        Returns:
            AttrDict: Response data with status code and content.

        """
        if not formatted_url:
            formatted_url = self.format_url(path)

        response = self.client.post(
            formatted_url,
            data=json.dumps(obj, default=str),
            headers=self.get_headers(),
            content_type="application/json",
        )
        return self.response(response, expected)

    def def_post_file(self, path, data, files, formatted_url=None, expected=None):
        """
        Send HTTP POST request with file upload to API endpoint.

        Args:
            path: API endpoint path.
            data: Request form data.
            files: Request files data (dict com {'csv_file': arquivo}).
            formatted_url: Pre-formatted URL (optional).
            expected: Expected status code (optional).

        Returns:
            AttrDict: Response data with status code and content.

        """
        if not formatted_url:
            formatted_url = self.format_url(path)

        # Passar autenticação como HTTP_AUTHORIZATION
        extra = {"HTTP_AUTHORIZATION": f"Token {self.token}"}

        # Unir data e arquivo
        data_envio = {**data, **files}

        response = self.client.post(
            formatted_url,
            data=data_envio,
            **extra,
        )
        return self.response(response, expected)

    @BaseTests.execute_before_and_after
    def post(self, path, obj, formatted_url=None, expected=None):
        """Send HTTP POST request with logging decorator."""
        return self.def_post(path, obj, formatted_url, expected)

    @BaseTests.execute_before_and_after
    def post_file(self, path, data, files, formatted_url=None, expected=None):
        """Send HTTP POST request with file upload and logging decorator."""
        return self.def_post_file(path, data, files, formatted_url, expected)

    @BaseTests.execute_before_and_after
    def get(self, path, formatted_url=None, expected=None):
        """
        Send HTTP GET request to API endpoint with logging.

        Args:
            path: API endpoint path.
            formatted_url: Pre-formatted URL (optional).
            expected: Expected status code (optional).

        Returns:
            AttrDict: Response data with status code and content.

        """
        if not formatted_url:
            formatted_url = self.format_url(path)
        response = self.client.get(formatted_url, headers=self.get_headers(), content_type="application/json")
        return self.response(response, expected)

    @BaseTests.execute_before_and_after
    def put(self, path, obj, formatted_url=None, expected=None):
        """
        Send HTTP PUT request to API endpoint with logging.

        Args:
            path: API endpoint path.
            obj: Request payload data.
            formatted_url: Pre-formatted URL (optional).
            expected: Expected status code (optional).

        Returns:
            AttrDict: Response data with status code and content.

        """
        if not formatted_url:
            formatted_url = self.format_url(path)

        response = self.client.put(
            formatted_url,
            data=json.dumps(obj, default=str),
            headers=self.get_headers(),
            content_type="application/json",
        )
        return self.response(response, expected)

    def response(self, response, expected):
        """
        Process response object and return formatted data.

        Args:
            response: HTTP response object.
            expected: Expected status code.

        Returns:
            AttrDict: Formatted response data with status code and content.

        """
        data = {
            "status_code": response.status_code,
            "content": response.content,
        }
        with contextlib.suppress(ValueError):
            data["content"] = response.json()

        method = response.request["REQUEST_METHOD"].upper()
        status_code_expected = expected or self.status_expected.get(
            method, self.status_expected.get(method.lower(), 200)
        )

        data["success"] = response.status_code == status_code_expected

        self.assert_values(data, response.status_code, status_code_expected)

        return self.AttrDict(data)

    def assert_values(self, data, status_code, status_code_expected):
        """
        Assert response status codes and log results.

        Args:
            data: Response data dictionary.
            status_code: Actual response status code.
            status_code_expected: Expected status code.

        """
        if self.logger:
            self.print_msg(data)
        try:
            self.assertEqual(status_code, status_code_expected)
        except AssertionError:
            self.print_error(data)
            self.assertEqual(status_code, status_code_expected)

    def get_path(self):
        """
        Return path for test execution.

        Returns:
            str: The test path.

        """
        return self.path

    def test_api_a_post(self) -> dict:
        """
        Test POST API endpoint if path, parameters, and POST method are available.

        Returns:
            dict: Response content if successful.

        """
        if not self.has_post():
            return

        path = self.get_path()

        if not path:
            self.assert_values({"content": "Path not found in method POST"}, 404, 201)
            return
        parameters = self.get_parameters()
        if parameters:
            return self.post(path, parameters)
        self.assert_values({"content": "Parameters not found in method POST"}, 404, 201)

    def test_api_b_get(self):
        """
        Test GET API endpoint if path exists and has GET capability.

        Returns:
            dict: Response content if successful.

        """
        if not self.has_get():
            return

        path = self.get_path()
        if path:
            return self.get(path)
        self.assert_values({"content": "Parameters not found in method GET"}, 404, 201)

    def test_api_c_put(self):
        """Test method to perform a PUT request if the path and parameters exist and has PUT capability."""
        if not self.has_put():
            return

        path = self.get_path()

        if not path:
            self.assert_values({"content": "Path not found in method PUT"}, 404, 201)
            return

        parameters = self.get_parameters()

        if parameters:
            return self.put(path, parameters)
        self.assert_values({"content": "Parameters not found in method PUT"}, 404, 201)

    @property
    def fake_password(self):
        """
        Generate and return a fake password for testing.

        Returns:
            str: A randomly generated password for test users.

        """
        if not self._fake_password:
            self._fake_password = f"@{secrets.token_urlsafe(16)}1&"
        return self._fake_password

    def create_user(self, username):
        """
        Create a user with the given username.

        Args:
            username (str): The username for the user.

        Returns:
            User: The created user object.

        """
        if username == "default":
            username = uuid.uuid4().hex
        user_create = User.objects.filter(username=username).first()
        email = f"{username}@example1.com"
        if not user_create:
            user_create = User()
        user_create.is_active = self.is_active
        user_create.is_superuser = self.is_superuser
        user_create.is_staff = self.is_staff
        user_create.status = "A"
        user_create.cpf = gerar_cpf()
        user_create.email = email
        user_create.username = username
        user_create.first_name = username
        user_create.save()

        user_create.groups.clear()
        groups = Group.objects.filter(name__in=self.group_names)
        self.assertEqual(
            groups.count(), len(self.group_names), msg="Number of groups does not match number of specified group names"
        )
        user_create.groups.add(*groups)
        self.client.logout()
        self.client.force_login(user_create)

        validate_password(self.fake_password)
        user_create.set_password(self.fake_password)
        user_create.save()
        return user_create

    def setUp(self):
        """
        Set up method for test class.

        Creates a test user if one doesn't exist already, logs in the user, and sets the
        `keep_db` flag based on command line arguments.
        """
        if self.set_user and not self.token:
            user = self.create_user(self.username)
            self.client.logout()
            self.client.force_login(user)
            self.user = user
