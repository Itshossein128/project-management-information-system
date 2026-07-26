# Events Module

This directory (`apps/api/core/events/`) manages background event publishing and consuming using RabbitMQ/Celery (message broker). It does not expose standard HTTP REST API endpoints.

## Purpose
- **publisher.py**: Functions to publish domain events (e.g., `project.created`, `wbs.updated`) to a message broker exchange.
- **consumer.py**: Background workers/consumers that listen to queues and process asynchronous tasks (e.g., triggering alerts, updating cache).
- **topology.py**: Definition of exchanges, queues, and routing keys.
