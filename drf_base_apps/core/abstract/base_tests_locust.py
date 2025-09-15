"""
The presented module imports classes and methods from other modules to define the standard behavior of load tests using the Locust tool.

It defines a main class (BaseTestsLocust) that extends an abstract class (BaseTests) and Locust's SequentialTaskSet class. Additionally, it includes a method to perform a GET request to an API endpoint using an authentication token defined in the TOKEN_TEST environment variable. The stop() method interrupts the execution of the test class if it reaches the maximum limit specified in the max_execution variable.
"""

import json
import os

from locust import SequentialTaskSet, between, task
from locust.exception import InterruptTaskSet

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "drf_base_config.settings")
import django

django.setup()
from drf_base_apps.core.abstract.base_tests import BaseTests
from drf_base_config.settings import BASE_API_URL, TOKEN_TEST


class BaseTestsLocust(BaseTests, SequentialTaskSet):
    """
    Define the base behavior of Locust's test classes.

    It extends the BaseTests abstract class and the SequentialTaskSet class from Locust.

    Attributes:
        abstract (bool): Indicates that this class is abstract.
        parameters (NoneType): Not used.
        wait_time (function): Defines the wait time after each task execution.
        min_wait (int): Minimum waiting time.
        counter (int): The number of executed tasks.

    Methods:
        __init__(*args, **kwargs): Constructor method. Initializes max_execution parameter from parent class.
        load_test_get(): Task to be executed during the load test. Makes a GET request to the API endpoint,
         using the token defined in TOKEN_TEST environment variable.
        stop(): Method to interrupt the execution of the test, based on the value of __max_execution parameter.

    """

    abstract = True
    parameters = {}
    wait_time = between(0.1, 5)
    min_wait = 0
    counter_get = 0
    counter_post = 0
    token = TOKEN_TEST
    base_url = BASE_API_URL

    def __init__(self, *args, **kwargs):
        """Initialize the BaseTestsLocust with execution limits and method names."""
        super().__init__(*args, **kwargs)
        self.__max_execution_get = self.parent.max_execution_get
        self.__max_execution_post = self.parent.max_execution_post
        self.__http_method_names = self.parent.http_method_names

    def setUp(self):
        """Set up the test environment."""
        pass

    def get_base_url(self):
        """Get the base URL for API testing."""
        return self.base_url

    @task(4)
    def task_post(self):
        """
        Send a HTTP POST request with payload `obj` to the API endpoint specified by `path`.

        Returns a dictionary with keys 'status_code' and 'content'.
        """
        if hasattr(self, "setUp"):
            self.setUp()

        if not self.habilited_run_post():
            self.stop()
            return

        self.counter_post += 1
        self.post()

    @BaseTests.execute_before_and_after
    def post(self):
        """Execute POST request to the API endpoint."""
        path = self.get_path()
        obj = self.get_parameters()

        if path and obj is not None and self.has_post():
            url = self.format_url(path)
            payload = json.dumps(obj, default=str)
            data = {"payload": payload, "url": url}
            response = self.client.post(url, payload, headers=self.get_headers(), verify=False)
            return self.return_response(data, response)

    @task(5)
    def task_get(self):
        """
        Execute task during the load test.

        Makes a GET request to the API endpoint, using the token defined in
        TOKEN_TEST environment variable.
        """
        if not self.habilited_run_get():
            self.stop()
            return

        self.counter_get += 1
        self.get()

    @BaseTests.execute_before_and_after
    def get(self):
        """Execute GET request to the API endpoint."""
        path = self.get_path()
        if path and self.has_get():
            if hasattr(self, "setUp"):
                self.setUp()
            url = self.format_url(path)
            data = {"payload": {}, "url": url}
            response = self.return_response(data, self.client.get(url, headers=self.get_headers(), verify=False))
            return response

    def habilited_run_get(self):
        """Check if GET requests are enabled based on execution limits."""
        if self.__max_execution_get == -1:
            return True
        return not self.counter_get >= self.__max_execution_get

    def habilited_run_post(self):
        """Check if POST requests are enabled based on execution limits."""
        if self.__max_execution_post == -1:
            return True
        return not self.counter_post >= self.__max_execution_post

    def stop(self):
        """Stop the test execution if limits are reached."""
        if not self.habilited_run_get() and not self.habilited_run_post():
            raise InterruptTaskSet()
