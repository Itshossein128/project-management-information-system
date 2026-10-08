from __future__ import annotations

from django.contrib.auth import get_user_model

from authentication.models import UserStatus
from config.exceptions import CodedValidationError
from master_data.models import OrganizationUnit

User = get_user_model()


def update_dossier(person: User, data: dict) -> User:
    if 'skills' in data:
        person.skills = data['skills']
    if 'qualifications' in data:
        person.qualifications = data['qualifications']
    if 'org_unit_id' in data:
        org_unit_id = data['org_unit_id']
        if org_unit_id is None:
            person.org_unit = None
        else:
            if not OrganizationUnit.objects.filter(pk=org_unit_id).exists():
                raise CodedValidationError(detail='Unknown organization unit.', code='validation_error')
            person.org_unit_id = org_unit_id
    if 'supervisor_id' in data:
        supervisor_id = data['supervisor_id']
        if supervisor_id is not None:
            if str(supervisor_id) == str(person.pk):
                raise CodedValidationError(detail='Supervisor cannot be self.', code='validation_error')
            if not User.objects.filter(pk=supervisor_id).exists():
                raise CodedValidationError(detail='Unknown supervisor.', code='validation_error')
        person.supervisor_id = supervisor_id
    if 'status' in data:
        person.status = data['status']
    if 'default_capacity_percent' in data:
        person.default_capacity_percent = data['default_capacity_percent']

    person.save()
    return person


def person_visible_in_project(person: User, project_id) -> bool:
    from hr.models import ResourceAllocation
    from master_data.models import ProjectMember

    if ProjectMember.objects.filter(project_id=project_id, user_id=person.id).exists():
        return True
    return ResourceAllocation.objects.filter(project_id=project_id, person_id=person.id, is_deleted=False).exists()
