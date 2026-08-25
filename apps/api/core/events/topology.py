"""RabbitMQ event topology and publisher."""

# Name of the central RabbitMQ topic exchange where events are published
TOPIC_EXCHANGE = 'ipcas.events'

# Allowed valid topic routing keys
BLUEPRINT_TOPICS = (
    'daily-report.approved',
    'cost.recorded',
    'ipc.submitted',
    'schedule.updated',
    'audit.log',
)

# Maps routing keys/topics to specific queue names for consumers
TOPIC_QUEUE_MAP = {
    'daily-report.approved': 'daily-report.approved.q',
    'cost.recorded': 'cost.recorded.q',
    'ipc.submitted': 'ipc.submitted.q',
    'schedule.updated': 'schedule.updated.q',
    'audit.log': 'audit.log.q',
}
