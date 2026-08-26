import pytest
from rest_framework.test import APIRequestFactory, force_authenticate
from procurement.views.report_views import ProcurementStatusReportView
from projects.models import Project
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.mark.django_db
class TestProcurementStatusReportView:
    def test_procurement_status_report_returns_200(self):
        user = User.objects.create(username="testuser", full_name="Test User")
        project = Project.objects.create(project_name="Test Project", project_code="PRJ-TEST")

        rf = APIRequestFactory()
        req = rf.get(f"/api/v1/projects/{project.id}/reports/procurement-status/")
        force_authenticate(req, user=user)

        view = ProcurementStatusReportView.as_view()
        response = view(req, project_pk=str(project.id))

        assert response.status_code == 200
        assert response.data["project_id"] == str(project.id)
        assert isinstance(response.data["summary"], list)
