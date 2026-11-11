import pytest
from django.contrib.auth.models import Group
from rest_framework.test import APIClient

from master_data.models import ManagedContractType, OrganizationUnit
from projects.models import Project
from projects.services import create_project_with_creator


def _client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_a7_p1_reference_project(auth_client, user, django_user_model):
    hr_group, _ = Group.objects.get_or_create(name='hr')
    hr = django_user_model.objects.create_user(
        username='a7p1-hr',
        mobile='+989121230701',
        password='password',
    )
    hr.groups.add(hr_group)
    hr_client = _client_for(hr)

    staff = django_user_model.objects.create_user(
        username='a7p1-staff',
        mobile='+989121230702',
        password='password',
        is_staff=True,
    )
    staff_denied = _client_for(staff).post(
        '/api/v1/organization-units/',
        {'code': 'A7P1-STF', 'name': 'Staff must not create'},
        format='json',
    )
    assert staff_denied.status_code == 403, staff_denied.content
    assert not OrganizationUnit.objects.filter(code='A7P1-STF').exists()

    unit = hr_client.post(
        '/api/v1/organization-units/',
        {'code': 'A7P1-OU', 'name': 'Reference owning unit'},
        format='json',
    )
    assert unit.status_code == 201, unit.content
    contract_type = hr_client.post(
        '/api/v1/contract-types/',
        {'code': 'A7P1-LUMP', 'name_fa': 'مبلغ مقطوع', 'name_en': 'Lump sum', 'is_active': True},
        format='json',
    )
    assert contract_type.status_code == 201, contract_type.content
    measure = hr_client.post(
        '/api/v1/measurement-units/',
        {'unit_name': 'A7P1 meter', 'unit_symbol': 'm'},
        format='json',
    )
    assert measure.status_code == 201, measure.content

    created = auth_client.post(
        '/api/v1/projects/',
        {
            'project_code': 'A7P1-REF',
            'project_name': 'A7 reference project',
            'employer': 'Reference employer',
            'start_date': '2026-01-15',
            'purpose': 'Prove the reference record',
            'scope_description': 'Three-level work breakdown',
            'main_deliverables': 'Identity, charter, and WBS',
            'contract_number': 'A7P1-C-1',
            'contract_amount': '2500000.00',
            'contract_type': 'A7P1-LUMP',
            'currency': 'IRR',
            'owning_unit': unit.json()['id'],
            'project_manager': str(user.id),
        },
        format='json',
    )
    assert created.status_code == 201, created.content
    project_id = created.json()['id']
    assert created.json()['status'] == 'draft'
    assert created.json()['owning_unit'] == unit.json()['id']
    assert created.json()['contract_type'] == 'A7P1-LUMP'

    reopened = auth_client.get(f'/api/v1/projects/{project_id}/')
    assert reopened.status_code == 200
    assert reopened.json()['project_name'] == 'A7 reference project'
    assert reopened.json()['scope_description'] == 'Three-level work breakdown'

    duplicate = auth_client.post(
        '/api/v1/projects/',
        {
            'project_code': 'A7P1-REF',
            'project_name': 'Duplicate',
            'employer': 'Other',
            'start_date': '2026-02-01',
        },
        format='json',
    )
    assert duplicate.status_code == 400, duplicate.content
    assert Project.objects.filter(project_code='A7P1-REF').count() == 1

    unknown = auth_client.post(
        '/api/v1/projects/',
        {
            'project_code': 'A7P1-BADTYPE',
            'project_name': 'Bad type',
            'employer': 'Other',
            'start_date': '2026-02-01',
            'contract_type': 'not-in-catalog',
        },
        format='json',
    )
    assert unknown.status_code == 400, unknown.content
    assert not Project.objects.filter(project_code='A7P1-BADTYPE').exists()

    charter_body = {
        'justification': 'Reference justification',
        'success_criteria': 'Fields reopen unchanged',
        'constraints': 'No importer rewrite',
        'assumptions': 'Approved access policy stands',
        'key_stakeholders_summary': 'Employer and project manager',
        'pm_authority': 'Day-to-day site decisions',
    }
    charter = auth_client.put(
        f'/api/v1/projects/{project_id}/kickoff-charter/',
        charter_body,
        format='json',
    )
    assert charter.status_code == 200, charter.content
    charter_get = auth_client.get(f'/api/v1/projects/{project_id}/kickoff-charter/')
    assert charter_get.status_code == 200
    for key, value in charter_body.items():
        assert charter_get.json()[key] == value

    root = auth_client.post(
        f'/api/v1/projects/{project_id}/wbs/',
        {
            'wbs_code': '1',
            'wbs_name': 'Project',
            'responsible': str(user.id),
            'acceptance_criteria': 'Scope agreed',
        },
        format='json',
    )
    assert root.status_code == 201, root.content
    phase = auth_client.post(
        f'/api/v1/projects/{project_id}/wbs/',
        {'parent_id': root.json()['wbs_id'], 'wbs_code': '1.1', 'wbs_name': 'Phase'},
        format='json',
    )
    assert phase.status_code == 201, phase.content
    package = auth_client.post(
        f'/api/v1/projects/{project_id}/wbs/',
        {
            'parent_id': phase.json()['wbs_id'],
            'wbs_code': '1.1.1',
            'wbs_name': 'Work package',
            'responsible': str(user.id),
            'acceptance_criteria': 'Package complete',
        },
        format='json',
    )
    assert package.status_code == 201, package.content
    tree = auth_client.get(f'/api/v1/projects/{project_id}/wbs/')
    assert tree.status_code == 200
    assert tree.json()[0]['wbs_code'] == '1'
    assert tree.json()[0]['children'][0]['wbs_code'] == '1.1'
    assert tree.json()[0]['children'][0]['children'][0]['acceptance_criteria'] == 'Package complete'

    duplicate_code = auth_client.post(
        f'/api/v1/projects/{project_id}/wbs/',
        {'wbs_code': '1', 'wbs_name': 'Again'},
        format='json',
    )
    assert duplicate_code.status_code == 400, duplicate_code.content

    other = auth_client.post(
        '/api/v1/projects/',
        {
            'project_code': 'A7P1-OTHER',
            'project_name': 'Other project',
            'employer': 'Other',
            'start_date': '2026-03-01',
        },
        format='json',
    )
    assert other.status_code == 201, other.content
    foreign = auth_client.post(
        f"/api/v1/projects/{other.json()['id']}/wbs/",
        {'parent_id': root.json()['wbs_id'], 'wbs_code': '9', 'wbs_name': 'Foreign parent'},
        format='json',
    )
    assert foreign.status_code == 400, foreign.content
    assert foreign.json()['error']['code'] == 'invalid_parent'

    cycle = auth_client.post(
        f"/api/v1/projects/{project_id}/wbs/{root.json()['wbs_id']}/move/",
        {'new_parent_id': package.json()['wbs_id'], 'position': 'last-child'},
        format='json',
    )
    assert cycle.status_code == 400, cycle.content
    assert 'wbs_cycle' in str(cycle.json())


@pytest.mark.django_db
def test_unchanged_legacy_contract_type_remains(auth_client, user):
    legacy = create_project_with_creator(
        creator=user,
        project_code='A7P1-LEGACY',
        project_name='Legacy type',
        employer='Employer',
        start_date='2026-01-01',
        contract_type='lump_sum',
    )
    assert not ManagedContractType.objects.filter(code='lump_sum').exists()
    same = auth_client.patch(
        f'/api/v1/projects/{legacy.id}/',
        {'contract_type': 'lump_sum'},
        format='json',
    )
    assert same.status_code == 200, same.content
    changed = auth_client.patch(
        f'/api/v1/projects/{legacy.id}/',
        {'contract_type': 'not-in-catalog'},
        format='json',
    )
    assert changed.status_code == 400, changed.content
    legacy.refresh_from_db()
    assert legacy.contract_type == 'lump_sum'


def _project_body(code, name):
    return {
        'project_code': code,
        'project_name': name,
        'employer': 'Employer',
        'start_date': '2026-04-01',
    }


@pytest.mark.django_db
def test_project_code_spaces_match_the_stored_code(auth_client, user):
    created = auth_client.post('/api/v1/projects/', _project_body('A7P1-SPACE', 'Space'), format='json')
    assert created.status_code == 201, created.content
    exact = auth_client.post('/api/v1/projects/', _project_body('A7P1-SPACE', 'Exact'), format='json')
    spaced = auth_client.post('/api/v1/projects/', _project_body('  A7P1-SPACE  ', 'Spaced'), format='json')
    assert exact.status_code == 400, exact.content
    assert spaced.status_code == 400, spaced.content
    assert spaced.json()['error']['message'] == exact.json()['error']['message']
    assert Project.objects.filter(project_code='A7P1-SPACE').count() == 1
    assert not Project.objects.filter(project_code='  A7P1-SPACE  ').exists()

    other = auth_client.post('/api/v1/projects/', _project_body('A7P1-SPACE2', 'Other'), format='json')
    assert other.status_code == 201, other.content
    renamed = auth_client.patch(
        f"/api/v1/projects/{other.json()['id']}/",
        {'project_code': ' A7P1-SPACE '},
        format='json',
    )
    assert renamed.status_code == 400, renamed.content
    assert renamed.json()['error']['message'] == exact.json()['error']['message']
    assert Project.objects.get(pk=other.json()['id']).project_code == 'A7P1-SPACE2'

    same = auth_client.patch(
        f"/api/v1/projects/{created.json()['id']}/",
        {'project_code': ' A7P1-SPACE '},
        format='json',
    )
    assert same.status_code == 200, same.content
    assert Project.objects.get(pk=created.json()['id']).project_code == 'A7P1-SPACE'

    create_project_with_creator(
        creator=user,
        project_code=' A7P1-PAD ',
        project_name='Padded legacy',
        employer='Employer',
        start_date='2026-04-02',
    )
    padded = auth_client.post('/api/v1/projects/', _project_body('A7P1-PAD', 'Unpadded'), format='json')
    assert padded.status_code == 400, padded.content
    assert padded.json()['error']['message'] == exact.json()['error']['message']
    assert not Project.objects.filter(project_code='A7P1-PAD').exists()
    assert Project.objects.filter(project_code=' A7P1-PAD ').count() == 1
