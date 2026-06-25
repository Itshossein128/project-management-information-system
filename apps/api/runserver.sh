#!/usr/bin/env bash
set -euo pipefail
DIR="$(dirname "$0")"
"$DIR/wait-for-postgres.sh"
exec "$DIR/django.sh" runserver "$@"
