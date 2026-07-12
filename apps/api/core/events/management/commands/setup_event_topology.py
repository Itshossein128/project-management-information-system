from django.core.management.base import BaseCommand

import pika

from events.publisher import declare_topology, get_rabbitmq_url


class Command(BaseCommand):
    help = 'Declare RabbitMQ exchanges, queues, and bindings for IPCAS blueprint topics.'

    def handle(self, *args, **options):
        connection = pika.BlockingConnection(pika.URLParameters(get_rabbitmq_url()))
        try:
            channel = connection.channel()
            declare_topology(channel)
        finally:
            connection.close()
        self.stdout.write(self.style.SUCCESS('RabbitMQ event topology declared.'))
