"""Private seeded failed attempts for real UI retry against the isolated API."""
import json
from pathlib import Path

from authentication.serializers import UserSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from django.utils import timezone
from schedule.models import MspImportJob
from schedule.tests.a7_p5_runtime_matrix import RuntimeMatrix, XML


def seed():
    runner=RuntimeMatrix('A7P5-BROWSER-', '/fixtures/plan.mpp')
    token=RefreshToken.for_user(runner.user)
    auth={'access':str(token.access_token),'refresh':str(token),'user':dict(UserSerializer(runner.user).data)}
    cases=[]
    for width in [1280,390]:
        for lang in ['en','fa']:
            p=runner.project()
            job=MspImportJob.objects.create(project=p,created_by=runner.user,status='failed',filename='plan.xml',file_data=XML,error_code='processing_interrupted',error_message='Processing was interrupted.',completed_at=timezone.now(),retention_anchor_at=timezone.now(),retention_anchor_source='terminal')
            cases.append({'width':width,'lang':lang,'project':str(p.id),'predecessor':str(job.id)})
    return {'auth':auth,'cases':cases}
