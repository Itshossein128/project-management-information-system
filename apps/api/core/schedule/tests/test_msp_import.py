"""MSP XML import parser tests (no database required)."""

import pytest

from schedule.services.msp_import import build_preview, parse_msp_xml

SAMPLE_MSP_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Tasks>
    <Task>
      <UID>1</UID>
      <ID>1</ID>
      <Name>Phase 1</Name>
      <OutlineLevel>1</OutlineLevel>
      <OutlineNumber>1</OutlineNumber>
      <WBS>1</WBS>
      <Summary>1</Summary>
    </Task>
    <Task>
      <UID>2</UID>
      <ID>2</ID>
      <Name>Sub phase</Name>
      <OutlineLevel>2</OutlineLevel>
      <OutlineNumber>1.1</OutlineNumber>
      <WBS>1.1</WBS>
      <Summary>1</Summary>
    </Task>
    <Task>
      <UID>3</UID>
      <ID>3</ID>
      <Name>Activity A</Name>
      <OutlineLevel>3</OutlineLevel>
      <OutlineNumber>1.1.1</OutlineNumber>
      <WBS>1.1.1</WBS>
      <Summary>0</Summary>
      <Duration>PT40H0M0S</Duration>
      <PercentComplete>25</PercentComplete>
      <Start>2026-01-01T08:00:00</Start>
      <Finish>2026-01-06T17:00:00</Finish>
      <PredecessorLink>
        <PredecessorUID>2</PredecessorUID>
        <Type>1</Type>
      </PredecessorLink>
    </Task>
  </Tasks>
</Project>
"""


def test_parse_msp_xml_extracts_tasks():
    result = parse_msp_xml(SAMPLE_MSP_XML)
    assert len(result.tasks) == 3
    activity = next(t for t in result.tasks if t.uid == '3')
    assert activity.duration_days == 5
    assert activity.percent_complete is not None


def test_parse_msp_xml_rejects_invalid_root():
    try:
        parse_msp_xml(b'<NotProject></NotProject>')
        assert False, 'expected ValueError'
    except ValueError as exc:
        assert 'Project' in str(exc)


def test_build_preview_returns_tree():
    parsed = parse_msp_xml(SAMPLE_MSP_XML)
    preview = build_preview(parsed)
    assert len(preview['wbs_tree']) >= 1
    assert len(preview['activities']) == 1
    assert isinstance(preview['warnings'], list)


def test_parse_msp_xml_blocks_billion_laughs():
    malicious_xml = b"""<?xml version="1.0"?>
<!DOCTYPE lolz [
 <!ENTITY lol "lol">
 <!ELEMENT lolz (#PCDATA)>
 <!ENTITY lol1 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">
 <!ENTITY lol2 "&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;&lol1;">
]>
<Project><Tasks><Task><Name>&lol2;</Name></Task></Tasks></Project>
"""
    try:
        parse_msp_xml(malicious_xml)
        assert False, 'expected ValueError due to defusedxml catching XML bomb'
    except ValueError as exc:
        assert str(exc) == 'Invalid XML'


@pytest.mark.django_db
class TestMspImportIntegration:
    def test_execute_msp_import_creates_activities(self, project, user):
        from projects.models import Activity
        from schedule.services.msp_import import execute_msp_import

        result = execute_msp_import(
            project,
            SAMPLE_MSP_XML,
            filename='sample.xml',
            replace=True,
            user=user,
        )
        assert result['activities_created'] >= 1
        assert Activity.objects.filter(project=project).exists()

    def test_msp_import_api_start_and_status(self, auth_client, project, settings):
        from django.core.files.uploadedfile import SimpleUploadedFile
        from schedule.models import MspImportJob

        settings.CELERY_TASK_ALWAYS_EAGER = True
        url = f'/api/v1/projects/{project.id}/import/msp/'
        upload = SimpleUploadedFile('sample.xml', SAMPLE_MSP_XML, content_type='application/xml')
        response = auth_client.post(
            url,
            {'file': upload, 'replace': 'true'},
            format='multipart',
        )
        assert response.status_code == 202
        job = MspImportJob.objects.get(pk=response.data['task_id'])
        status_url = f'/api/v1/projects/{project.id}/import/msp/status/{job.id}/'
        status_resp = auth_client.get(status_url)
        assert status_resp.status_code == 200
        assert status_resp.data['status'] in ('done', 'running', 'pending')
