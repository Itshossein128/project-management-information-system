"""P6 XER import tests."""

import pytest

from schedule.services.p6_import import parse_p6_xer


SAMPLE_XER = b"""ERMHDR\t18.8\t2024-01-01\tProject
%T\tPROJWBS
%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\tseq_num
%R\t1\t\t1\tProject Root\t1
%R\t2\t1\t1.1\tPhase 1\t2
%T\tTASK
%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt
%R\t100\t2\tA100\tExcavation\t40
%T\tTASKPRED
%F\ttask_id\tpred_task_id\tpred_type\tlag_hr_cnt
"""


@pytest.mark.django_db
class TestP6ImportParser:
    def test_parse_minimal_xer(self):
        result = parse_p6_xer(SAMPLE_XER)
        assert len(result.tasks) >= 2
        assert any(t.is_summary for t in result.tasks)
        assert any(not t.is_summary for t in result.tasks)

    def test_invalid_xer_raises(self):
        with pytest.raises(ValueError):
            parse_p6_xer(b'not an xer file')


@pytest.mark.django_db
class TestP6ImportIntegration:
    def test_execute_p6_import_creates_activities(self, project, user):
        from projects.models import Activity
        from schedule.services.p6_import import execute_p6_import

        result = execute_p6_import(
            project,
            SAMPLE_XER,
            filename='sample.xer',
            replace=True,
            user=user,
        )
        assert result['activities_created'] >= 1
        assert Activity.objects.filter(project=project).exists()

    def test_p6_import_api_start(self, auth_client, project, settings):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from schedule.models import P6ImportJob

        settings.CELERY_TASK_ALWAYS_EAGER = True
        url = f'/api/v1/projects/{project.id}/import/p6/'
        upload = SimpleUploadedFile('sample.xer', SAMPLE_XER, content_type='application/octet-stream')
        response = auth_client.post(
            url,
            {'file': upload, 'replace': 'true'},
            format='multipart',
        )
        assert response.status_code == 202
        assert P6ImportJob.objects.filter(pk=response.data['task_id']).exists()
