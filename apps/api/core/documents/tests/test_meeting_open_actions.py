"""FR-COL US1: meeting actions and open-actions report."""

from datetime import date, timedelta

import pytest


@pytest.mark.django_db
def test_meeting_nested_actions_and_open_report(auth_client, project, user):
    meeting_resp = auth_client.post(
        f'/api/v1/projects/{project.id}/meetings/',
        {
            'meeting_date': '2026-10-01',
            'meeting_type': 'weekly_progress',
            'decisions': 'Proceed with slab pour',
        },
        format='json',
    )
    assert meeting_resp.status_code == 201, meeting_resp.content
    meeting_id = meeting_resp.json()['id']

    base = f'/api/v1/projects/{project.id}/meetings/{meeting_id}/actions/'
    a1 = auth_client.post(
        base,
        {
            'description': 'Issue RFI for slab edge',
            'owner': str(user.id),
            'due_date': '2026-10-20',
        },
        format='json',
    )
    assert a1.status_code == 201, a1.content
    assert a1.json()['status'] == 'open'

    a2 = auth_client.post(
        base,
        {
            'description': 'Confirm rebar delivery',
            'owner': str(user.id),
        },
        format='json',
    )
    assert a2.status_code == 201, a2.content

    open_resp = auth_client.get(f'/api/v1/projects/{project.id}/meeting-actions/open/')
    assert open_resp.status_code == 200
    results = open_resp.json()['results']
    assert len(results) == 2
    descriptions = {r['description'] for r in results}
    assert 'Issue RFI for slab edge' in descriptions
    assert 'Confirm rebar delivery' in descriptions


@pytest.mark.django_db
def test_done_action_leaves_open_report_and_overdue_filter(auth_client, project, user):
    meeting_resp = auth_client.post(
        f'/api/v1/projects/{project.id}/meetings/',
        {
            'meeting_date': '2026-10-01',
            'meeting_type': 'other',
            'decisions': 'Notes',
        },
        format='json',
    )
    assert meeting_resp.status_code == 201
    meeting_id = meeting_resp.json()['id']
    base = f'/api/v1/projects/{project.id}/meetings/{meeting_id}/actions/'

    past = (date.today() - timedelta(days=3)).isoformat()
    future = (date.today() + timedelta(days=10)).isoformat()

    overdue_action = auth_client.post(
        base,
        {'description': 'Overdue task', 'due_date': past},
        format='json',
    )
    assert overdue_action.status_code == 201
    overdue_id = overdue_action.json()['id']

    open_future = auth_client.post(
        base,
        {'description': 'Future task', 'due_date': future},
        format='json',
    )
    assert open_future.status_code == 201
    future_id = open_future.json()['id']

    patch = auth_client.patch(
        f'/api/v1/projects/{project.id}/meeting-actions/{future_id}/',
        {'status': 'done'},
        format='json',
    )
    assert patch.status_code == 200
    assert patch.json()['status'] == 'done'
    assert patch.json().get('completed_at') is not None

    open_all = auth_client.get(f'/api/v1/projects/{project.id}/meeting-actions/open/')
    assert open_all.status_code == 200
    ids = {r['id'] for r in open_all.json()['results']}
    assert overdue_id in ids
    assert future_id not in ids

    overdue_only = auth_client.get(
        f'/api/v1/projects/{project.id}/meeting-actions/open/?overdue=true'
    )
    assert overdue_only.status_code == 200
    overdue_results = overdue_only.json()['results']
    assert len(overdue_results) == 1
    assert overdue_results[0]['id'] == overdue_id
    assert overdue_results[0].get('is_overdue') is True
