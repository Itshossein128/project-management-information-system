"""Seed synthetic A6-P1 actors in an explicitly named isolated database only."""
import json
import os
import sys
import uuid
from pathlib import Path

root = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(root / 'apps/api/core'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.db import transaction
from inventory.models import Category, Item
from master_data.models import ProjectMember, ProjectMemberRole, ProjectMemberPermissionOverride, ProjectPosition, Role, RolePermission
from permissions.constants import DEFAULT_ROLE_PERMISSIONS
from projects.models import Activity, Project
from wbs.services import create_wbs_node
from authentication.utils import get_tokens_for_user

name = settings.DATABASES['default']['NAME']
if not name.startswith('velora_a6_p1_e2e_') or os.environ.get('A6_P1_E2E_DB') != name:
    raise SystemExit('Refusing to seed: DATABASE_URL and A6_P1_E2E_DB must match an isolated velora_a6_p1_e2e_* database')
run = uuid.uuid4().hex[:8]
password = 'A6-Only-E2E-123!'
User = get_user_model()
with transaction.atomic():
    groups = {key: Group.objects.get_or_create(name=key)[0] for key in ('admin', 'visitor', 'hr', 'manager')}
    users = {}
    for i, kind in enumerate(('manager', 'visitor', 'inactive', 'staff', 'hr', 'admin', 'superuser', 'editor', 'target', 'new', 'writer'), 1):
        # Synthetic usernames are unique on every run; no existing credentials are changed.
        user = User.objects.create_user(username=f'a6p1_{run}_{kind}', mobile=f'+199{int(run,16):010d}{i:02d}', full_name=f'A6 {run} {kind}', password=password)
        if kind in groups:
            user.groups.add(groups[kind])
        if kind in ('staff', 'superuser'):
            user.is_staff = True
        if kind == 'superuser':
            user.is_superuser = True
        user.save()
        users[kind] = user
    roles = {}
    for role_name in ('project_manager', 'viewer'):
        role, _ = Role.objects.get_or_create(role_name=role_name)
        for codename in DEFAULT_ROLE_PERMISSIONS[role_name]:
            RolePermission.objects.get_or_create(role=role, permission_codename=codename)
        roles[role_name] = role
    editor_role = Role.objects.create(role_name=f'a6edit_{run}')
    for codename in ('view_project', 'view_wbs', 'view_activities', 'edit_activities'):
        RolePermission.objects.create(role=editor_role, permission_codename=codename)
    # This role is deleted while the browser has an old selection, reproducing a genuine race.
    temporary_roles = {lang: Role.objects.create(role_name=f'a6race_{run}_{lang}') for lang in ('fa', 'en')}
    a = Project.objects.create(project_code=f'A6A{run}', project_name=f'A6-P1 A {run}', status='active')
    b = Project.objects.create(project_code=f'A6B{run}', project_name=f'A6-P1 B {run}', status='active')
    def join(project, user, role, state='active'):
        member = ProjectMember.objects.create(project=project, user=user, status=state)
        ProjectMemberRole.objects.create(member=member, role=role)
        return member
    join(a, users['manager'], roles['project_manager'])
    join(b, users['manager'], roles['viewer'])
    join(a, users['inactive'], roles['viewer'], 'inactive')
    join(a, users['editor'], editor_role)
    target_member = join(a, users['target'], roles['viewer'])
    ProjectMemberPermissionOverride.objects.create(member=target_member, permission_codename='edit_wbs', is_granted=False)
    position = ProjectPosition.objects.create(project=a, position_name=f'A6 position {run}', slug=f'a6-{run}')
    wbs, _ = create_wbs_node(project_id=a.id, wbs_code='1', wbs_name='A6 root')
    activity = Activity.objects.create(project=a, wbs=wbs, activity_code='A6-1', activity_name='A6 activity', total_quantity=100, created_by=users['editor'], updated_by=users['editor'])
    category = Category.objects.create(name=f'A6 category {run}')
    item = Item.objects.create(name=f'A6 item {run}', quantity=2, category=category)
    payload = {'run':run, 'password':password, 'users':{k:{'id':str(v.pk),'username':v.username,'mobile':v.mobile,'name':v.full_name} for k,v in users.items()}, 'tokens':{k:get_tokens_for_user(v)['access'] for k,v in users.items()}, 'project_a':str(a.id), 'project_b':str(b.id), 'position':str(position.id), 'activity':str(activity.id), 'viewer_role':str(roles['viewer'].id), 'temporary_roles':{k:{'id':str(v.id),'name':v.role_name} for k,v in temporary_roles.items()}, 'category':category.id, 'item':item.id}
    print(json.dumps(payload))
