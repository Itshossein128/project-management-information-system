"""Known lifecycle events and actors for status undo contracts."""
from uuid import uuid4
from projects.tests.archive_restore_helpers import actor, client_for, ready_project, state, base, populate_business_records, business_snapshot
from projects import lifecycle_service as lifecycle

def source_project(user, operation='resume', origin='active'):
    project = ready_project(user)
    if operation == 'resume' or origin == 'suspended':
        project = lifecycle.suspend(project, user)
    if operation == 'undo_completion':
        project = lifecycle.complete(project, user)
    return project

def preview(client, project, operation='resume'):
    route = 'resume-preview/' if operation == 'resume' else 'undo-completion-preview/'
    return client.get(base(project) + route)

def confirmed_body(client, project, operation='resume', reason='Selected by mistake'):
    response = preview(client, project, operation)
    assert response.status_code == 200, response.data
    return {'request_id': str(uuid4()), 'confirmation_token': response.data['confirmation_token'], 'reason': reason}

def member(user, project, *codes):
    from master_data.models import ProjectMember, ProjectMemberPermissionOverride
    row = ProjectMember.objects.create(user=user, project=project, status='active')
    for code in codes:
        ProjectMemberPermissionOverride.objects.create(member=row, permission_codename=code, is_granted=True)
    return row
