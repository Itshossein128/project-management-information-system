"""Keep migration-owned RBAC catalog available in reused transaction-test databases."""
import importlib
import pytest
from django.apps import apps

@pytest.fixture(scope='session', autouse=True)
def decision_support_test_catalog(django_db_setup,django_db_blocker):
    seed=importlib.import_module('master_data.migrations.0013_decision_support_permissions').seed_decision_support_permissions
    with django_db_blocker.unblock():
        seed(apps,None)
    yield
    # TransactionTestCase flushes migration data; restore only the test catalog,
    # so a later --reuse-db invocation is not missing permission fixtures.
    with django_db_blocker.unblock():
        seed(apps,None)

@pytest.fixture(autouse=True)
def decision_support_transaction_catalog(request, django_db_setup, django_db_blocker):
    """A prior transaction test may have flushed the migration-owned roles."""
    marker = request.node.get_closest_marker("django_db")
    if marker and marker.kwargs.get("transaction"):
        with django_db_blocker.unblock():
            importlib.import_module("master_data.migrations.0013_decision_support_permissions").seed_decision_support_permissions(apps, None)
