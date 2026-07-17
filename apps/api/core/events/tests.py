import json
from unittest import mock

from django.test import TestCase, override_settings

from events.consumer import dispatch_message, handle_daily_report_approved
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


class DailyReportApprovedHandlerTests(TestCase):
    @mock.patch('field_reports.tasks.recalculate_activity_progress.delay')
    def test_handler_enqueues_progress_recalc(self, mock_delay):
        handle_daily_report_approved({
            'topic': 'daily-report.approved',
            'project_id': 'p1',
            'payload': {'report_id': 'r1'},
        })
        mock_delay.assert_called_once_with('r1')

    @mock.patch('field_reports.tasks.recalculate_activity_progress.delay')
    def test_dispatch_routes_to_handler(self, mock_delay):
        dispatch_message(
            'daily-report.approved',
            {'payload': {'report_id': 'r2'}},
        )
        mock_delay.assert_called_once_with('r2')

    @mock.patch('field_reports.tasks.recalculate_activity_progress.delay')
    def test_handler_skips_missing_report_id(self, mock_delay):
        handle_daily_report_approved({'payload': {}})
        mock_delay.assert_not_called()
