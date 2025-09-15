"""Tests for user management functionality."""

from drf_base_apps.core.abstract.tests import AbstractTest


class TestUserForbiddenDetail(AbstractTest):
    """
    Test class for the 'user detail' endpoint.

    This class contains tests for the PUT method of the 'user detail' endpoint,
    focusing on verifying the behavior of stop voting.

    Attributes:
        path (str): The endpoint path being tested.
        http_method_names (list): List of HTTP methods allowed for testing.
        parameters (dict): Dictionary containing parameters for the PUT request.

    Methods:
        test_api_c_put: Test method to verify the correctness of the PUT request.

    """

    path = "user-detail"
    http_method_names = ["get"]
    status_expected = {"get": 403}
