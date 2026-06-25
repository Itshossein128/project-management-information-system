import json
import logging
import os
from typing import Any

import pika

from .topology import BLUEPRINT_TOPICS, TOPIC_EXCHANGE, TOPIC_QUEUE_MAP

logger = logging.getLogger(__name__)


def get_rabbitmq_url() -> str:
    return os.environ.get('RABBITMQ_URL', 'amqp://ipcas:ipcas@localhost:5672/')


def declare_topology(channel) -> None:
    channel.exchange_declare(exchange=TOPIC_EXCHANGE, exchange_type='topic', durable=True)
    for topic in BLUEPRINT_TOPICS:
        queue = TOPIC_QUEUE_MAP[topic]
        channel.queue_declare(queue=queue, durable=True)
        channel.queue_bind(exchange=TOPIC_EXCHANGE, queue=queue, routing_key=topic)
    logger.info('Declared RabbitMQ topology: exchange=%s topics=%s', TOPIC_EXCHANGE, BLUEPRINT_TOPICS)


class EventPublisher:
    def __init__(self, url: str | None = None):
        self.url = url or get_rabbitmq_url()

    def publish(self, topic: str, payload: dict[str, Any], project_id: str | None = None) -> None:
        if topic not in BLUEPRINT_TOPICS:
            raise ValueError(f'Unknown topic: {topic}')
        body = json.dumps({'topic': topic, 'project_id': project_id, 'payload': payload})
        connection = pika.BlockingConnection(pika.URLParameters(self.url))
        try:
            channel = connection.channel()
            declare_topology(channel)
            channel.basic_publish(
                exchange=TOPIC_EXCHANGE,
                routing_key=topic,
                body=body.encode('utf-8'),
                properties=pika.BasicProperties(delivery_mode=2, content_type='application/json'),
            )
            logger.info('Published event topic=%s project_id=%s', topic, project_id)
        finally:
            connection.close()
