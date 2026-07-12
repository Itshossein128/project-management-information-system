from io import StringIO

import pytest

from contracts.models import Contract
from projects.models import Activity


@pytest.mark.django_db
def test_seed_contracts_demo(project, user, activity, wbs):
    from django.core.management import call_command

    out = StringIO()
    call_command('seed_contracts_demo', project_id=str(project.id), user_id=str(user.id), stdout=out)
    assert Contract.objects.filter(project=project, contract_number='DEMO-MAIN-001').exists()
    assert 'Demo contracts seeded' in out.getvalue()


@pytest.mark.django_db
def test_seed_contracts_demo_requires_activities(project, user):
    from django.core.management import call_command

    Activity.objects.filter(project=project).delete()
    out = StringIO()
    err = StringIO()
    call_command('seed_contracts_demo', project_id=str(project.id), stdout=out, stderr=err)
    assert 'No activities found' in err.getvalue()
