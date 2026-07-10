import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.core.management import call_command
from django.core.management.base import CommandError

from projects.management.commands.verify_blueprint_schema import BLUEPRINT_TABLES

def test_verify_blueprint_schema_success():
    out = StringIO()
    err = StringIO()

    mock_models = []
    for table in BLUEPRINT_TABLES:
        mock_model = MagicMock()
        mock_model._meta.db_table = table
        mock_models.append(mock_model)

    with patch('projects.management.commands.verify_blueprint_schema.apps.get_models', return_value=mock_models):
        call_command('verify_blueprint_schema', stdout=out, stderr=err)

        output = out.getvalue()
        assert "All blueprint tables present." in output

def test_verify_blueprint_schema_missing_tables():
    out = StringIO()
    err = StringIO()

    mock_model1 = MagicMock()
    mock_model1._meta.db_table = 'users'
    mock_model2 = MagicMock()
    mock_model2._meta.db_table = 'projects'

    with patch('projects.management.commands.verify_blueprint_schema.apps.get_models', return_value=[mock_model1, mock_model2]):
        with pytest.raises(SystemExit) as excinfo:
            call_command('verify_blueprint_schema', stdout=out, stderr=err)

        assert excinfo.value.code == 1

        error_output = err.getvalue()
        assert "Missing:" in error_output
