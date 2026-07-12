#!/usr/bin/env bash
# Shared helpers for customer launcher scripts.

set -euo pipefail

customer_root_dir() {
  cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd
}

customer_load_config() {
  local root config_file
  root="$(customer_root_dir)"
  config_file="${root}/customer/ipcas.config"

  GIT_REMOTE="${GIT_REMOTE:-origin}"
  GIT_BRANCH="${GIT_BRANCH:-main}"
  APP_URL="${APP_URL:-http://localhost:8080}"
  HEALTH_URL="${HEALTH_URL:-http://localhost:8080/api/schema/}"
  WAIT_INTERVAL_SEC="${WAIT_INTERVAL_SEC:-2}"
  WAIT_MAX_ATTEMPTS="${WAIT_MAX_ATTEMPTS:-90}"
  COMPOSE_PROJECT_NAME="${COMPOSE_PROJECT_NAME:-ipcas}"

  if [[ -f "${config_file}" ]]; then
    # shellcheck disable=SC1090
    source "${config_file}"
  fi

  export GIT_REMOTE GIT_BRANCH APP_URL HEALTH_URL WAIT_INTERVAL_SEC WAIT_MAX_ATTEMPTS
  export COMPOSE_PROJECT_NAME
}

customer_compose_cmd() {
  if docker compose version >/dev/null 2>&1; then
    echo "docker compose"
  elif command -v docker-compose >/dev/null 2>&1; then
    echo "docker-compose"
  else
    echo "Docker Compose is not installed. Install Docker Desktop, then try again." >&2
    exit 1
  fi
}

customer_compose() {
  local root compose_cmd
  root="$(customer_root_dir)"
  compose_cmd="$(customer_compose_cmd)"
  (
    cd "${root}"
    export COMPOSE_PROJECT_NAME
    # shellcheck disable=SC2086
    ${compose_cmd} -f docker-compose.customer.yml "$@"
  )
}

customer_ensure_env() {
  local root env_file example_file
  root="$(customer_root_dir)"
  env_file="${root}/.env"
  example_file="${root}/.env.customer.example"

  if [[ ! -f "${env_file}" ]]; then
    if [[ ! -f "${example_file}" ]]; then
      echo "Missing ${example_file}" >&2
      exit 1
    fi
    cp "${example_file}" "${env_file}"
    echo "Created .env from .env.customer.example"
  fi
}

customer_check_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "Docker is not installed. Install Docker Desktop, then try again." >&2
    exit 1
  fi

  if ! docker info >/dev/null 2>&1; then
    echo "Docker is not running. Open Docker Desktop, wait until it is ready, then try again." >&2
    exit 1
  fi
}

customer_check_git() {
  local root
  root="$(customer_root_dir)"

  if ! command -v git >/dev/null 2>&1; then
    echo "Git is not installed. Install Git, then try again." >&2
    exit 1
  fi

  if [[ ! -d "${root}/.git" ]]; then
    echo "This folder is not a Git repository." >&2
    echo "Clone the project first, for example:" >&2
    echo "  git clone <repository-url> building-management" >&2
    exit 1
  fi
}

customer_open_browser() {
  local url="${1:-${APP_URL:-http://localhost:8080}}"

  if command -v xdg-open >/dev/null 2>&1; then
    xdg-open "${url}" >/dev/null 2>&1 || true
  elif command -v open >/dev/null 2>&1; then
    open "${url}" || true
  else
    echo "Open ${url} in your browser."
  fi
}

customer_is_stack_up() {
  curl -sf "${HEALTH_URL:-http://localhost:8080/api/schema/}" >/dev/null 2>&1
}
