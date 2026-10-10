# Server deployment

Apply the production overlay to the customer stack. Keep the existing `.env`
and Docker volumes when updating an installation.

Required public settings in `.env`:

```dotenv
DEBUG=false
SEED_DEMO_DATA=false
VITE_API_BASE_URL=/api
FRONTEND_URL=http://SERVER_IP
ALLOWED_HOSTS=SERVER_IP,localhost,127.0.0.1,api,traefik
CORS_ALLOWED_ORIGINS=http://SERVER_IP
AWS_S3_PUBLIC_ENDPOINT_URL=http://SERVER_IP:9000
VELORA_API_IMAGE=ipcas-api:RELEASE
VELORA_WEB_IMAGE=ipcas-web:RELEASE
```

Set strong `SECRET_KEY`, PostgreSQL, RabbitMQ, and S3 credentials separately.
For existing databases and storage, retain their credentials during an update.
The S3 endpoint must be reachable from both the API container and the browser:
the application uploads and downloads files directly using signed URLs. Port
9000 serves the S3 API; the MinIO management console remains internal.

From the repository root, after backing up the database, uploads, and `.env`:

```bash
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml config --quiet
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml build api web
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml run --rm --no-deps api python manage.py migrate --noinput
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml run --rm --no-deps api python manage.py setup_event_topology
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml up -d --no-build --wait --wait-timeout 120 postgres rabbitmq redis minio api worker celery-worker celery-beat web traefik
docker compose -f docker-compose.customer.yml -f docker-compose.production.yml ps
```

Migrations run once explicitly; application and worker containers skip them.
API health checks use `/api/health/`, which checks PostgreSQL and Redis. Web
health checks use `/login`. App logs rotate at 10 MB with three files retained.
Celery Beat runs scheduled jobs with a persistent schedule file.

The IP deployment uses HTTP. For trusted HTTPS, configure a domain and a valid
certificate for both the application and its S3 endpoint. The customer Traefik
configuration contains a legacy domain; do not assume that its bundled
certificate is trusted or that it covers a server IP.

Keep release image tags and database backups for rollback. Recreate services
with the previous image tags and configuration; restore a database backup only
if an incompatible migration requires it. Never use `down -v` during updates.
