import pytest
from django.utils import timezone

from decision_support.models import DecisionCase, DecisionRun


@pytest.mark.django_db
def test_decision_case_and_run_defaults(project, user):
    case = DecisionCase.objects.create(
        project=project,
        title='Contractor selection',
        created_by=user,
        updated_by=user,
    )
    assert case.selected_methods == []
    assert case.criteria == []
    assert case.alternatives == []
    assert case.weights == []
    assert case.types == []
    assert case.performance_matrix == []
    assert case.ahp_matrix == []
    assert case.dematel_matrix == []
    assert case.ism_matrix == []

    run = DecisionRun.objects.create(
        case=case,
        project=project,
        method='saw',
        input_snapshot={'criteria': ['a']},
        result={'status': 'stub', 'engine': None},
        extracted_at=timezone.now(),
        extracted_by=user,
    )
    assert run.method == 'saw'
    assert run.input_snapshot['criteria'] == ['a']
    assert run.extracted_by_id == user.id
