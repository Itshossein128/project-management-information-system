from django.core.management.base import BaseCommand

from events.consumer import run_consumer


class Command(BaseCommand):
    help = 'Run RabbitMQ event consumer worker for IPCAS blueprint topics.'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting event worker...'))
        run_consumer()
