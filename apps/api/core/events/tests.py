import json
from unittest import mock

from django.test import TestCase, override_settings

from events.publisher import EventPublisher, declare_topology, get_rabbitmq_url
from events.topology import TOPIC_QUEUE_MAP


@override_settings(
    RABBITMQ_URL='amqp://guest:guest@localhost:5672/',
)
class EventPublisherTests(TestCase):
    @mock.patch('events.publisher.pika.BlockingConnection')
    def test_publish_declares_topology(self, mock_conn_cls):
        channel = mock.Mock()
        mock_conn_cls.return_value.channel.return_value = channel
        EventPublisher(url='amqp://guest:guest@localhost:5672/').publish(
            'daily-report.approved',
            {'report_id': 'test'},
            project_id='00000000-0000-0000-0000-000000000001',
        )
        channel.exchange_declare.assert_called()
        channel.basic_publish.assert_called_once()
        body = channel.basic_publish.call_args.kwargs['body']
        payload = json.loads(body.decode())
        self.assertEqual(payload['topic'], 'daily-report.approved')
        self.assertEqual(len(TOPIC_QUEUE_MAP), 5)
