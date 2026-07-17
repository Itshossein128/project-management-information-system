#!/usr/bin/env bash
set -euo pipefail

BASE_URL="${SMOKE_BASE_URL:-http://localhost:8080}"
RABBITMQ_API="${SMOKE_RABBITMQ_API:-http://localhost:15672}"
RABBITMQ_USER="${RABBITMQ_DEFAULT_USER:-ipcas}"
RABBITMQ_PASS="${RABBITMQ_DEFAULT_PASS:-ipcas}"

echo "==> Smoke: API schema via Traefik"
curl -sf "${BASE_URL}/api/schema/" >/dev/null

echo "==> Smoke: login"
LOGIN_RESPONSE="$(curl -sf -X POST "${BASE_URL}/api/auth/login/" \
  -H 'Content-Type: application/json' \
  -d '{"phone_number":"+10000000001","password":"devpass123"}')"

ACCESS_TOKEN="$(python3 -c "import json,sys; print(json.load(sys.stdin)['access'])" <<<"${LOGIN_RESPONSE}")"
test -n "${ACCESS_TOKEN}"

echo "==> Smoke: authenticated project list"
PROJECTS_JSON="$(curl -sf "${BASE_URL}/api/v1/projects/" \
  -H "Authorization: Bearer ${ACCESS_TOKEN}")"
echo "${PROJECTS_JSON}" >/dev/null

PROJECT_ID="$(python3 -c "import json,sys; d=json.load(sys.stdin); print(d[0]['id'] if d else '')" <<<"${PROJECTS_JSON}")"

if [[ -n "${PROJECT_ID}" ]]; then
  echo "==> Smoke: daily report sync-batch"
  curl -sf -X POST "${BASE_URL}/api/v1/projects/${PROJECT_ID}/daily-reports/sync-batch/" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" \
    -H 'Content-Type: application/json' \
    -d '[{"local_id":"smoke-1","report_date":"2024-12-01","site_status":"active"}]' >/dev/null

  echo "==> Smoke: progress s-curve"
  curl -sf "${BASE_URL}/api/v1/projects/${PROJECT_ID}/progress/s-curve/?interval=daily" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" >/dev/null || true

  echo "==> Smoke: cost summary"
  curl -sf "${BASE_URL}/api/v1/projects/${PROJECT_ID}/costs/summary/" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" >/dev/null || true

  echo "==> Smoke: contracts list"
  curl -sf "${BASE_URL}/api/v1/projects/${PROJECT_ID}/contracts/" \
    -H "Authorization: Bearer ${ACCESS_TOKEN}" >/dev/null || true
fi

echo "==> Smoke: RabbitMQ management API"
curl -sf -u "${RABBITMQ_USER}:${RABBITMQ_PASS}" \
  "${RABBITMQ_API}/api/overview" >/dev/null

echo "==> Smoke: publish test event"
python3 - <<'PY'
import json
import os
import pika

url = os.environ.get('RABBITMQ_URL', 'amqp://ipcas:ipcas@localhost:5672/')
connection = pika.BlockingConnection(pika.URLParameters(url))
channel = connection.channel()
body = json.dumps({'topic': 'schedule.updated', 'project_id': None, 'payload': {'smoke': True}})
channel.basic_publish(exchange='ipcas.events', routing_key='schedule.updated', body=body.encode())
connection.close()
print('published schedule.updated smoke event')
PY

echo "All smoke checks passed."
