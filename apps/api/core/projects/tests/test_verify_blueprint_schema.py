import pytest
from io import StringIO
from unittest.mock import patch, MagicMock
from django.core.management import call_command

from projects.management.commands.verify_blueprint_schema import BLUEPRINT_TABLES


def test_verify_blueprint_schema_real_models():
    """Run against actual Django models — should pass when schema is complete."""
    out = StringIO()
    err = StringIO()
    call_command('verify_blueprint_schema', stdout=out, stderr=err)
    output = out.getvalue()
    assert 'All blueprint tables present.' in output
    assert f'Found {len(BLUEPRINT_TABLES)}/{len(BLUEPRINT_TABLES)} blueprint tables.' in output


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
        assert 'Missing:' in err.getvalue()
