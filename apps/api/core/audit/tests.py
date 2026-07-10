from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from audit.middleware import AuditLogMiddleware
from audit.models import AuditLog

User = get_user_model()


class AuditLogRedactionTests(APITestCase):
    def test_redacts_sensitive_auth_fields(self):
        payload = {
            'username': 'auditor',
            'password': 'plain-text',
            'access_token': 'jwt-access',
            'refresh_token': 'jwt-refresh',
            'profile': {'api_secret': 'shh'},
        }
        redacted = AuditLogMiddleware._redact_data(payload)
        self.assertEqual(redacted['username'], 'auditor')
        self.assertEqual(redacted['password'], '***REDACTED***')
        self.assertEqual(redacted['access_token'], '***REDACTED***')
        self.assertEqual(redacted['refresh_token'], '***REDACTED***')
        self.assertEqual(redacted['profile']['api_secret'], '***REDACTED***')

    def test_preserves_non_sensitive_fields(self):
        payload = {
            'access_level': 'admin',
            'refresh_rate': 30,
            'items': [{'name': 'bolt', 'client_secret': 'hidden'}],
        }
        redacted = AuditLogMiddleware._redact_data(payload)
        self.assertEqual(redacted['access_level'], 'admin')
        self.assertEqual(redacted['refresh_rate'], 30)
        self.assertEqual(redacted['items'][0]['name'], 'bolt')
        self.assertEqual(redacted['items'][0]['client_secret'], '***REDACTED***')


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
