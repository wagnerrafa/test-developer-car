"""
Abstract test classes for the application.

This module provides abstract classes for testing. If the script is run with 'manage.py',
it uses BaseTestsDjango class from core.abstract.base_tests_django module. Otherwise, it uses BaseTestsLocust
class from core.abstract.base_tests_locust module.

The base define what the type of test will be. BaseTestsDjango tests the endpoints and does the validations.
BaseTestsLocust performs load testing on endpoints, simulates multiple users and measures how the platform is
doing.

Classes:
    - AbstractTest: An abstract test class that inherits from BaseTestsDjango or BaseTestsLocust,
      depending on the script being run.
    - AbstractTestHR: Abstract test class for HR users.
    - AbstractTestCLB: Abstract test class for CLB users.
    - AbstractTestIntranet: Abstract test class for INTRANET users.
"""

from drf_base_apps.core.abstract.base_tests_django import BaseTestsDjango


class BaseAbstractTest(BaseTestsDjango):
    """
    Abstract test class for Django testing.

    This class inherits from BaseTestsDjango and provides a base for testing
    endpoints and performing validations.
    """

    class Meta:
        """Meta class for the application abstract test class."""

        abstract = True


class AbstractTest(BaseAbstractTest):
    """
    Abstract test class for Django testing.

    This class inherits from BaseTestsDjango and provides a base for testing
    endpoints and performing validations.
    """

    is_superuser = False
