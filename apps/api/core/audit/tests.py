from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from audit.models import AuditLog

User = get_user_model()


@override_settings(AUDIT_LOG_ASYNC=False)
class AuditLogMiddlewareTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='auditor',
            password='secure-pass-123',
            mobile='09111111111',
            full_name='Auditor',
        )
        Group.objects.get_or_create(name='business-setup')
        self.user.groups.add(Group.objects.get(name='business-setup'))
        login = self.client.post(
            reverse('authentication:login'),
            {'username': 'auditor', 'password': 'secure-pass-123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')

    def test_successful_post_creates_audit_log(self):
        before = AuditLog.objects.count()
        response = self.client.post(
            reverse('project-list'),
            {
                'project_code': 'AUD-001',
                'project_name': 'Audit Test Project',
                'employer': 'Test Employer',
                'start_date': '2024-01-01',
            },
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(AuditLog.objects.count(), before + 1)
        entry = AuditLog.objects.latest('created_at')
        self.assertEqual(entry.actor_id, self.user.id)
        self.assertEqual(entry.http_method, 'POST')
        self.assertIn('/api/v1/projects/', entry.path)

    def test_failed_request_does_not_create_audit_log(self):
        before = AuditLog.objects.count()
        response = self.client.post(
            reverse('project-list'),
            {'project_name': 'Missing code'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(AuditLog.objects.count(), before)


class ResolveResourceTests(APITestCase):
    def test_resolve_project_path(self):
        from audit.resolve_resource import resolve_resource
        import uuid

        project_id = uuid.uuid4()
        path = f'/api/v1/projects/{project_id}/'
        resolved = resolve_resource(path, project_id=project_id)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved.resource_type, 'project')
        self.assertEqual(resolved.resource_id, project_id)
