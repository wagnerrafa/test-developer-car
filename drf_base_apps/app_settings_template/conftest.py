"""Setup pytest handler commands."""

import pytest
from django.core.management import call_command
from django.db import connection


@pytest.fixture(scope="session", autouse=True)
def setup_groups(django_db_setup, django_db_blocker):
    """Executa create_groups antes de todos os testes."""
    with django_db_blocker.unblock():
        call_command("create_groups", verbosity=1)
        connection.ensure_connection()
