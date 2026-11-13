#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")/../.."
ops/a7-p5/prepare-host.sh
if [[ ! -f ops/a7-p5/.env.acceptance ]]; then
  cp ops/a7-p5/.env.acceptance.example ops/a7-p5/.env.acceptance
  chmod 600 ops/a7-p5/.env.acceptance
fi
compose=(docker compose --env-file ops/a7-p5/.env.acceptance -f ops/a7-p5/compose.yml)
args=()
if [[ -n ${A7P5_BUILD_PROXY:-} ]]; then
  args+=(--build-arg "HTTP_PROXY=$A7P5_BUILD_PROXY" --build-arg "HTTPS_PROXY=$A7P5_BUILD_PROXY")
fi
"${compose[@]}" config --quiet
"${compose[@]}" build "${args[@]}" api
"${compose[@]}" up -d --no-build --pull never
ready=false
for n in {1..15}; do
  if "${compose[@]}" exec -T api python manage.py verify_import_runtime --preflight --output /tmp/a7p5-preflight.json; then
    ready=true
    break
  fi
  sleep 2
done
[[ "$ready" == true ]] || { echo 'Isolated preflight did not become ready' >&2; exit 1; }
matrix_status=0
"${compose[@]}" exec -T api python manage.py verify_import_runtime --run-matrix --reference /fixtures/plan.mpp --project-prefix A7P5-RUNTIME- --output /tmp/a7p5-runtime.json || matrix_status=$?
mkdir -p specs/055-a7-p5-import-operations/evidence/runtime
"${compose[@]}" exec -T api cat /tmp/a7p5-preflight.json > specs/055-a7-p5-import-operations/evidence/runtime/preflight.json
"${compose[@]}" exec -T api cat /tmp/a7p5-runtime.json > specs/055-a7-p5-import-operations/evidence/runtime/manifest.json
exit "$matrix_status"
