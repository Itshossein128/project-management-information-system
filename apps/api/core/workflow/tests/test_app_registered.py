"""FR-COL: workflow Django app is registered."""

from django.conf import settings

from workflow.apps import WorkflowConfig


def test_workflow_app_importable_and_installed():
    assert WorkflowConfig.name == 'workflow'
    assert 'workflow' in settings.INSTALLED_APPS
