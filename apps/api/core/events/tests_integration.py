import json
import os
import unittest

import pika
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from django.test import override_settings
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from events.publisher import EventPublisher, declare_topology, get_rabbitmq_url
from events.topology import TOPIC_QUEUE_MAP
from master_data.models import ProjectMember

User = get_user_model()

RABBITMQ_URL = os.environ.get('RABBITMQ_URL', '')
MINIO_CONFIGURED = bool(os.environ.get('AWS_S3_ENDPOINT_URL'))


def rabbitmq_available() -> bool:
    if not RABBITMQ_URL:
        return False
    try:
        connection = pika.BlockingConnection(pika.URLParameters(RABBITMQ_URL))
        connection.close()
        return True
    except Exception:
        return False


@unittest.skipUnless(rabbitmq_available(), 'RabbitMQ is not available')
@override_settings(RABBITMQ_URL=RABBITMQ_URL or 'amqp://ipcas:ipcas@localhost:5672/')
class EventPublisherIntegrationTests(APITestCase):
    def test_publish_delivers_to_queue(self):
        connection = pika.BlockingConnection(pika.URLParameters(get_rabbitmq_url()))
        channel = connection.channel()
        declare_topology(channel)
        queue = TOPIC_QUEUE_MAP['daily-report.approved']
        channel.queue_purge(queue=queue)

        EventPublisher().publish(
            'daily-report.approved',
            {'report_id': 'integration-test'},
            project_id='00000000-0000-0000-0000-000000000099',
        )

        method, properties, body = channel.basic_get(queue=queue, auto_ack=True)
        connection.close()
        self.assertIsNotNone(method)
        payload = json.loads(body.decode('utf-8'))
        self.assertEqual(payload['topic'], 'daily-report.approved')
        self.assertEqual(payload['payload']['report_id'], 'integration-test')


@unittest.skipUnless(rabbitmq_available(), 'RabbitMQ is not available')
@override_settings(RABBITMQ_URL=RABBITMQ_URL or 'amqp://ipcas:ipcas@localhost:5672/', AUDIT_LOG_ASYNC=False)
class ProjectCreateEventIntegrationTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            username='publisher',
            password='secure-pass-123',
            mobile='09222222222',
            full_name='Publisher',
        )
        Group.objects.get_or_create(name='business-setup')
        self.user.groups.add(Group.objects.get(name='business-setup'))
        login = self.client.post(
            reverse('authentication:login'),
            {'username': 'publisher', 'password': 'secure-pass-123'},
            format='json',
        )
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {login.data["access"]}')

    def test_project_create_publishes_schedule_updated(self):
        connection = pika.BlockingConnection(pika.URLParameters(get_rabbitmq_url()))
        channel = connection.channel()
        declare_topology(channel)
        queue = TOPIC_QUEUE_MAP['schedule.updated']
        channel.queue_purge(queue=queue)

        response = self.client.post(
            reverse('project-list'),
            {'project_code': 'evt-001', 'project_name': 'Event Test', 'employer': 'Test', 'start_date': '2023-01-01'},
            format='json',
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        method, properties, body = channel.basic_get(queue=queue, auto_ack=True)
        connection.close()
        self.assertIsNotNone(method)
        payload = json.loads(body.decode('utf-8'))
        self.assertEqual(payload['topic'], 'schedule.updated')
        self.assertEqual(payload['payload']['action'], 'created')
