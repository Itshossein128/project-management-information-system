"""Read-only domain/job snapshot for isolated browser acceptance; no credentials output."""
import json
import os
import subprocess
import sys
from uuid import UUID

project_id = str(UUID(sys.argv[1]))
script = '''
import json
from django.db import connection
from django.core.serializers.json import DjangoJSONEncoder
from projects.models import Project, WBS, Activity, ActivityRelation, ProjectKickoffCharter
from schedule.models import BaselineSchedule, BaselineActivity, MspImportJob, P6ImportJob
assert 'a7p5' in connection.settings_dict['NAME'], 'isolated database required'
pid = %r
queries = {'project': Project.objects.filter(pk=pid), 'charter': ProjectKickoffCharter.objects.filter(project_id=pid), 'wbs': WBS.objects.filter(project_id=pid), 'activities': Activity.objects.filter(project_id=pid), 'relations': ActivityRelation.objects.filter(successor__project_id=pid), 'baselines': BaselineSchedule.objects.filter(project_id=pid), 'baseline_activities': BaselineActivity.objects.filter(baseline__project_id=pid)}
result = {name: list(query.order_by('pk').values()) for name, query in queries.items()}
# Include all jobs, even terminal ones, to detect jobs accidentally created by preview.
for name, model in [('msp_jobs', MspImportJob), ('p6_jobs', P6ImportJob)]:
    result[name] = list(model.objects.filter(project_id=pid).order_by('pk').values_list('pk', flat=True))
print(json.dumps(result, cls=DjangoJSONEncoder))
''' % project_id
result = subprocess.run(['docker', 'exec', '-i', os.environ.get('A7P6_API_CONTAINER', 'a7p5-import-api-1'), 'python', 'manage.py', 'shell'], input=script, text=True, capture_output=True, check=True)
print(json.dumps(json.loads(result.stdout.strip().splitlines()[-1])))
