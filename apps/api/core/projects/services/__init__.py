"""Project creation and membership business rules."""
import secrets
from datetime import timedelta
from uuid import UUID

from django.contrib.auth import get_user_model
from django.db import IntegrityError, transaction
from django.utils import timezone

from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole, Role
from projects.models import Project

User = get_user_model()


def attach_creator_as_member(*, project: Project, creator: User) -> ProjectMember:
    """Make creator an active project_manager member (idempotent if already member)."""
    member, _created = ProjectMember.objects.get_or_create(
        project=project,
        user=creator,
        defaults={'status': MemberStatus.ACTIVE},
    )
    if member.status != MemberStatus.ACTIVE:
        member.status = MemberStatus.ACTIVE
        member.save(update_fields=['status'])

    pm_role = Role.objects.filter(role_name='project_manager').first()
    if pm_role and not member.member_roles.filter(role=pm_role).exists():
        ProjectMemberRole.objects.create(member=member, role=pm_role)

    if project.project_manager_id is None:
        project.project_manager = creator
        project.save(update_fields=['project_manager'])

    return member


@transaction.atomic
def create_project_with_creator(*, creator: User, **project_fields) -> Project:
    project = Project.objects.create(**project_fields)
    attach_creator_as_member(project=project, creator=creator)
    from procurement.services.workshop_block_service import ensure_workshop_block

    ensure_workshop_block(project, created_by=creator)
    return project


class PositionSelectionError(Exception):
    def __init__(self, position_ids: list):
        self.position_ids = list(position_ids)
        super().__init__(self.position_ids)


class RoleProjectMismatch(Exception):
    def __init__(self, role_ids: list):
        self.role_ids = list(role_ids)
        super().__init__(self.role_ids)


class UnknownRoles(Exception):
    """One or more submitted role ids are not assignable."""

    def __init__(self, missing_ids: list):
        self.missing_ids = list(missing_ids)
        super().__init__(self.missing_ids)


def missing_role_ids(role_ids) -> list:
    """Return submitted ids that do not refer to an existing role, in order."""
    if not role_ids:
        return []
    requested = []
    invalid = []
    for raw in role_ids:
        try:
            requested.append(raw if isinstance(raw, UUID) else UUID(str(raw)))
        except (TypeError, ValueError):
            invalid.append(raw)
    found = set(Role.objects.filter(id__in=requested).values_list('id', flat=True))
    missing = [item for item in requested if item not in found]
    return invalid + missing


def replace_member_positions(member: ProjectMember, position_ids: list, actor=None) -> None:
    """Select several job titles without changing access roles."""
    from master_data.models import ProjectPosition
    from permissions.role_services import record_access_change
    from permissions.services import get_inherited_codenames

    requested = list(dict.fromkeys(position_ids))
    positions = list(ProjectPosition.objects.filter(id__in=requested))
    found = {position.id for position in positions}
    if len(found) != len(requested):
        raise PositionSelectionError([item for item in requested if item not in found])
    rejected = [
        position.id
        for position in positions
        if (not position.is_active)
        or (position.project_id is not None and position.project_id != member.project_id)
    ]
    if rejected:
        raise PositionSelectionError(rejected)
    before_ids = sorted(str(position_id) for position_id in member.positions.values_list('id', flat=True))
    before_permissions = sorted(get_inherited_codenames(member))
    member.positions.set(positions)
    member.position = positions[0] if positions else None
    member.save(update_fields=['position'])
    member = ProjectMember.objects.get(pk=member.pk)
    after_ids = sorted(str(position.id) for position in positions)
    after_permissions = sorted(get_inherited_codenames(member))
    if before_ids != after_ids or before_permissions != after_permissions:
        record_access_change(
            actor=actor,
            project=member.project,
            subject_user=member.user,
            role=None,
            action='positions_replaced',
            before={'position_ids': before_ids, 'permissions': before_permissions},
            after={'position_ids': after_ids, 'permissions': after_permissions},
        )


def assign_roles_to_member(member: ProjectMember, role_ids: list, actor=None) -> None:
    """Replace member roles only when every submitted id exists and belongs here."""
    from permissions.role_services import record_access_change
    from permissions.services import get_inherited_codenames

    missing = missing_role_ids(role_ids)
    if missing:
        raise UnknownRoles(missing)
    roles = list(Role.objects.filter(id__in=role_ids))
    seen = set()
    unique_roles = []
    for role in roles:
        if role.id in seen:
            continue
        seen.add(role.id)
        unique_roles.append(role)
    mismatched = [
        role.id for role in unique_roles
        if role.project_id is not None and role.project_id != member.project_id
    ]
    if mismatched:
        raise RoleProjectMismatch(mismatched)
    before_roles = sorted(str(role_id) for role_id in member.member_roles.values_list('role_id', flat=True))
    before_permissions = sorted(get_inherited_codenames(member))
    member.member_roles.all().delete()
    ProjectMemberRole.objects.bulk_create(
        [ProjectMemberRole(member=member, role=role) for role in unique_roles]
    )
    member = ProjectMember.objects.get(pk=member.pk)
    after_roles = sorted(str(role.id) for role in unique_roles)
    after_permissions = sorted(get_inherited_codenames(member))
    if before_roles != after_roles or before_permissions != after_permissions:
        record_access_change(
            actor=actor,
            project=member.project,
            subject_user=member.user,
            role=unique_roles[0] if len(unique_roles) == 1 else None,
            action='roles_replaced',
            before={'role_ids': before_roles, 'permissions': before_permissions},
            after={'role_ids': after_roles, 'permissions': after_permissions},
        )


class AlreadyMember(Exception):
    """One person already has a membership in this project."""


class InvitationInvalid(Exception):
    """The invitation cannot grant access."""


def _history(*, actor, project, subject_user, action, before, after) -> None:
    from permissions.role_services import record_access_change

    record_access_change(
        actor=actor,
        project=project,
        subject_user=subject_user,
        role=None,
        action=action,
        before=before,
        after=after,
    )


def _apply_roles_and_titles(member, role_ids, position_ids, actor) -> None:
    assign_roles_to_member(member, role_ids, actor=actor)
    if position_ids:
        replace_member_positions(member, position_ids, actor=actor)


def create_project_member(*, project_id, actor, user_id=None, email='', mobile='', role_ids=None, position_ids=None):
    """Create one membership or one invitation. A conflict leaves no partial roles."""
    role_ids = list(role_ids or [])
    position_ids = list(position_ids or [])
    try:
        with transaction.atomic():
            if user_id:
                user = User.objects.get(pk=user_id)
                if ProjectMember.objects.filter(project_id=project_id, user=user).exists():
                    raise AlreadyMember()
                member = ProjectMember.objects.create(
                    project_id=project_id,
                    user=user,
                    status=MemberStatus.ACTIVE,
                )
                _apply_roles_and_titles(member, role_ids, position_ids, actor)
                return member
            address_email = (email or '').strip()
            address_mobile = (mobile or '').strip()
            from authentication.services import _hash_token
            from notifications.services.delivery import deliver_account_message

            missing = missing_role_ids(role_ids)
            if missing:
                raise UnknownRoles(missing)
            if position_ids:
                from master_data.models import ProjectPosition
                requested = list(dict.fromkeys(position_ids))
                positions = list(ProjectPosition.objects.filter(id__in=requested))
                found = {position.id for position in positions}
                if len(found) != len(requested):
                    raise PositionSelectionError([item for item in requested if item not in found])
                rejected = [
                    position.id for position in positions
                    if (not position.is_active)
                    or (position.project_id is not None and str(position.project_id) != str(project_id))
                ]
                if rejected:
                    raise PositionSelectionError(rejected)
            now = timezone.now()
            stale = ProjectMember.objects.filter(
                project_id=project_id,
                user__isnull=True,
                status=MemberStatus.INVITED,
                invite_cancelled_at__isnull=True,
                invite_expires_at__lt=now,
            )
            if address_email:
                stale.filter(invited_email__iexact=address_email).update(
                    invite_cancelled_at=now, invite_token_hash='',
                )
            if address_mobile:
                stale.filter(invited_mobile=address_mobile).update(
                    invite_cancelled_at=now, invite_token_hash='',
                )
            raw_token = secrets.token_urlsafe(32)
            recipient = address_email or address_mobile
            delivery_status = deliver_account_message(
                recipient=recipient,
                subject='Project invitation',
                body=raw_token,
            )
            member = ProjectMember.objects.create(
                project_id=project_id,
                user=None,
                invited_email=address_email,
                invited_mobile=address_mobile,
                status=MemberStatus.INVITED,
                invite_expires_at=timezone.now() + timedelta(days=7),
                invite_token_hash=_hash_token(raw_token),
                delivery_status=delivery_status,
            )
            _apply_roles_and_titles(member, role_ids, position_ids, actor)
            _history(
                actor=actor,
                project=member.project,
                subject_user=None,
                action='invitation_created',
                before={},
                after={
                    'status': member.status,
                    'delivery_status': delivery_status,
                    'invited_email': address_email,
                    'invited_mobile': address_mobile,
                },
            )
            return member
    except IntegrityError as exc:
        raise AlreadyMember() from exc


def connect_invitation(*, project_id, member_id, user_id, actor, role_ids=None, position_ids=None):
    from authentication.services import account_can_authenticate

    try:
        return _connect_invitation(
            project_id, member_id, user_id, actor, account_can_authenticate, role_ids, position_ids,
        )
    except IntegrityError as exc:
        raise AlreadyMember() from exc


def _require_open_invitation(member) -> None:
    if member.user_id is not None or member.status != MemberStatus.INVITED:
        raise InvitationInvalid()
    if member.invite_accepted_at is not None or member.invite_cancelled_at is not None:
        raise InvitationInvalid()
    if member.invite_expires_at is None or member.invite_expires_at <= timezone.now():
        raise InvitationInvalid()


def _connect_invitation(project_id, member_id, user_id, actor, account_can_authenticate, role_ids=None, position_ids=None):
    with transaction.atomic():
        member = ProjectMember.objects.select_for_update().get(pk=member_id, project_id=project_id)
        _require_open_invitation(member)
        user = User.objects.get(pk=user_id)
        if ProjectMember.objects.filter(project_id=project_id, user=user).exclude(pk=member.pk).exists():
            raise AlreadyMember()
        before_status = member.status
        member.user = user
        member.invite_accepted_at = timezone.now()
        member.invite_token_hash = ''
        if account_can_authenticate(user):
            member.status = MemberStatus.ACTIVE
        member.save(update_fields=['user', 'invite_accepted_at', 'invite_token_hash', 'status'])
        if role_ids is not None:
            _apply_roles_and_titles(member, role_ids, position_ids or [], actor)
        _history(
            actor=actor,
            project=member.project,
            subject_user=user,
            action='invitation_accepted',
            before={'status': before_status},
            after={'status': member.status, 'user_id': str(user.pk)},
        )
        return member


def cancel_invitation(*, project_id, member_id, actor):
    with transaction.atomic():
        member = ProjectMember.objects.select_for_update().get(pk=member_id, project_id=project_id)
        if member.user_id is not None or member.invite_cancelled_at is not None:
            raise InvitationInvalid()
        member.invite_cancelled_at = timezone.now()
        member.invite_token_hash = ''
        member.save(update_fields=['invite_cancelled_at', 'invite_token_hash'])
        _history(
            actor=actor,
            project=member.project,
            subject_user=None,
            action='invitation_cancelled',
            before={'status': member.status},
            after={
                'cancelled': True,
                'member_id': str(member.pk),
                'invited_email': member.invited_email,
                'invited_mobile': member.invited_mobile,
            },
        )
        return member


def accept_invitation(*, token: str, user):
    from authentication.services import _hash_token, account_can_authenticate

    token_hash = _hash_token(token or '')
    with transaction.atomic():
        member = (
            ProjectMember.objects.select_for_update()
            .filter(
                invite_token_hash=token_hash,
                invite_cancelled_at__isnull=True,
                invite_accepted_at__isnull=True,
            )
            .exclude(invite_token_hash='')
            .first()
        )
        if member is None or member.invite_expires_at is None or member.invite_expires_at <= timezone.now():
            raise InvitationInvalid()
        email = (member.invited_email or '').strip().lower()
        mobile = (member.invited_mobile or '').strip()
        user_email = (user.email or '').strip().lower()
        user_mobile = (user.mobile or '').strip()
        matches = (email and user_email == email) or (mobile and user_mobile == mobile)
        if not matches:
            raise InvitationInvalid()
        if ProjectMember.objects.filter(project_id=member.project_id, user=user).exclude(pk=member.pk).exists():
            raise AlreadyMember()
        before_status = member.status
        member.user = user
        member.invite_accepted_at = timezone.now()
        member.invite_token_hash = ''
        if account_can_authenticate(user):
            member.status = MemberStatus.ACTIVE
        member.save(update_fields=['user', 'invite_accepted_at', 'invite_token_hash', 'status'])
        _history(
            actor=user,
            project=member.project,
            subject_user=user,
            action='invitation_accepted',
            before={'status': before_status},
            after={'status': member.status},
        )
        return member


def change_member_status(member, status: str, actor) -> None:
    if status == member.status:
        return
    before = member.status
    member.status = status
    member.save(update_fields=['status'])
    _history(
        actor=actor,
        project=member.project,
        subject_user=member.user,
        action='member_status_changed',
        before={'status': before},
        after={'status': status},
    )
