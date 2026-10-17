"""Create test-only JWT actors on an explicitly disposable restore database."""
import json, os
from pathlib import Path
import django

django.setup()
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework_simplejwt.tokens import RefreshToken

assert settings.DATABASES['default']['NAME'].startswith('velora_restore_'), 'Refusing fixture writes outside the disposable restore database'
actors={}
for name,superuser,admin in [('creator',False,True),('administrator',False,True),('superuser',True,False),('ordinary',False,False),('approver',False,False),('viewer',False,False),('outsider',False,False)]:
 user,_=get_user_model().objects.get_or_create(username='status-undo-'+name,defaults={'full_name':'Restore '+name,'is_superuser':superuser,'is_staff':superuser})
 user.is_superuser=superuser;user.is_staff=superuser;user.save(update_fields=['is_superuser','is_staff'])
 user.groups.clear()
 if admin:user.groups.add(Group.objects.get_or_create(name='admin')[0])
 token=RefreshToken.for_user(user)
 actors[name]={'access':str(token.access_token),'refresh':str(token),'user':{'id':str(user.pk),'full_name':user.full_name,'roles':list(user.groups.values_list('name',flat=True))}}
p=Path(__file__).resolve().parents[2]/'test-results/status-undo-actors.json';p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(actors));p.chmod(0o600)
print('Disposable browser actors saved in ignored test-results (tokens not printed).')
