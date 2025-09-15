"""
Custom test runner for Django applications.

This module provides a custom test runner that extends Django's DiscoverRunner
to provide additional filtering and customization of test execution.
"""

from django.test.runner import DiscoverRunner


class CustomTestRunner(DiscoverRunner):
    """
    Custom test runner that filters tests based on specific criteria.

    This test runner extends Django's DiscoverRunner to filter out certain test classes
    and organize tests by HTTP method type.
    """

    def load_tests_for_label(self, label, discover_kwargs):
        """
        Load tests for a given label with custom filtering.

        This method filters tests before they are counted, so the "Found X test(s)."
        message will show the correct filtered count.
        """
        all_tests = super().load_tests_for_label(label, discover_kwargs)

        if not all_tests:
            return all_tests

        # Filter the tests before returning
        filtered_tests = []
        for tests in all_tests:

            try:
                for build_test in tests:

                    if "AbstractTest" in str(build_test):
                        continue
                    if "BaseTestsDjango" in str(build_test):
                        continue

                    try:
                        for test in build_test._tests:

                            has_test = self.has_method(test)

                            if has_test:
                                filtered_tests.append(test)
                    except (AttributeError, TypeError):
                        has_test = self.has_method(build_test)

                        if has_test:
                            filtered_tests.append(build_test)
            except (AttributeError, TypeError):
                has_test = self.has_method(tests)

                if has_test:
                    filtered_tests.append(tests)
        # Create a new test suite with filtered tests
        new_suite = self.test_suite()
        for test in filtered_tests:
            new_suite.addTest(test)

        return new_suite

    def has_method(self, test):
        """Check if test has method."""
        if not str(test).startswith("test_"):
            return False

        if str(test).endswith("post)") and "post" in test.http_method_names:
            return True

        if str(test).endswith("get)") and "get" in test.http_method_names:
            return True

        return str(test).endswith("put)") and "put" in test.http_method_names
