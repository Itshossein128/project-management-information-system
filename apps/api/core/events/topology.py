"""RabbitMQ event topology and publisher."""

TOPIC_EXCHANGE = 'ipcas.events'

BLUEPRINT_TOPICS = (
    'daily-report.approved',
    'cost.recorded',
    'ipc.submitted',
    'schedule.updated',
    'audit.log',
)

TOPIC_QUEUE_MAP = {
    'daily-report.approved': 'daily-report.approved.q',
    'cost.recorded': 'cost.recorded.q',
    'ipc.submitted': 'ipc.submitted.q',
    'schedule.updated': 'schedule.updated.q',
    'audit.log': 'audit.log.q',
}
