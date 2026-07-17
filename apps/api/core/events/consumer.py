"""RabbitMQ event consumers and topic handlers."""
import json
import logging
import signal
from typing import Any, Callable

import pika

from audit.service import persist_audit_log
from events.publisher import declare_topology, get_rabbitmq_url
from events.topology import TOPIC_QUEUE_MAP

logger = logging.getLogger(__name__)

_shutdown = False


def _handle_shutdown(signum, frame):
    global _shutdown
    _shutdown = True
    logger.info('Shutdown signal received (%s)', signum)


def handle_audit_log(envelope: dict[str, Any]) -> None:
    payload = envelope.get('payload') or {}
    persist_audit_log(payload)


def handle_default(topic: str, envelope: dict[str, Any]) -> None:
    logger.info('Received event topic=%s project_id=%s', topic, envelope.get('project_id'))


def handle_daily_report_approved(envelope: dict[str, Any]) -> None:
    """Enqueue progress recalculation when a daily report is approved."""
    payload = envelope.get('payload') or {}
    report_id = payload.get('report_id')
    if not report_id:
        logger.warning('daily-report.approved missing report_id in payload')
        return
    from field_reports.tasks import recalculate_activity_progress

    recalculate_activity_progress.delay(str(report_id))


TOPIC_HANDLERS: dict[str, Callable[[dict[str, Any]], None]] = {
    'audit.log': handle_audit_log,
    'daily-report.approved': handle_daily_report_approved,
}


def dispatch_message(topic: str, envelope: dict[str, Any]) -> None:
    handler = TOPIC_HANDLERS.get(topic, lambda env: handle_default(topic, env))
    handler(envelope)


def _on_message(channel, method, properties, body):
    routing_key = method.routing_key
    try:
        envelope = json.loads(body.decode('utf-8'))
        topic = envelope.get('topic') or routing_key
        dispatch_message(topic, envelope)
        channel.basic_ack(delivery_tag=method.delivery_tag)
    except Exception:
        logger.exception('Failed to process message routing_key=%s', routing_key)
        channel.basic_nack(delivery_tag=method.delivery_tag, requeue=False)


def run_consumer(url: str | None = None) -> None:
    global _shutdown
    signal.signal(signal.SIGTERM, _handle_shutdown)
    signal.signal(signal.SIGINT, _handle_shutdown)

    connection = pika.BlockingConnection(pika.URLParameters(url or get_rabbitmq_url()))
    channel = connection.channel()
    declare_topology(channel)

    channel.basic_qos(prefetch_count=10)
    for queue_name in TOPIC_QUEUE_MAP.values():
        channel.basic_consume(queue=queue_name, on_message_callback=_on_message)

    logger.info('Event worker consuming queues: %s', list(TOPIC_QUEUE_MAP.values()))
    try:
        while not _shutdown:
            connection.process_data_events(time_limit=1)
    finally:
        logger.info('Stopping event worker')
        connection.close()
