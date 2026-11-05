"""Run A6-P1 browser tests against a new, isolated PostgreSQL database."""
import os
import signal
import socket
import subprocess
import sys
import tempfile
import time
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from urllib.request import ProxyHandler, build_opener

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[2]
API = ROOT / 'apps/api/core'
PYTHON = ROOT / 'apps/api/.venv/bin/python'
url = os.environ.get('DATABASE_URL')
if not url:
    raise SystemExit('Set DATABASE_URL first; see e2e/a6-p1/README.md')
parts = urlsplit(url)
name = f'velora_a6_p1_e2e_{int(time.time())}_{os.getpid()}'
env = os.environ.copy()
env.update(DATABASE_URL=urlunsplit(parts._replace(path='/' + name)), A6_P1_E2E_DB=name,
           DJANGO_SETTINGS_MODULE='a6_p1_test_settings',
           PYTHONPATH=str(ROOT / 'e2e/a6-p1') + os.pathsep + env.get('PYTHONPATH', ''),
           AUDIT_LOG_ASYNC='false', CELERY_TASK_ALWAYS_EAGER='true')

def port():
    with socket.socket() as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]

def ready(url, process):
    for _ in range(120):
        if process.poll() is not None:
            raise RuntimeError(f'Service stopped during startup: {url}')
        try:
            with build_opener(ProxyHandler({})).open(url, timeout=2):
                return
        except Exception:
            time.sleep(.5)
    raise RuntimeError(f'Service failed to start: {url}')

processes = []
config_path = ROOT / f'apps/web/node_modules/.cache/a6-p1-{os.getpid()}.config.ts'
try:
    with psycopg.connect(url, autocommit=True) as conn:
        with conn.cursor() as cursor:
            cursor.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    print(f'Created isolated database: {name}', flush=True)
    subprocess.run([str(PYTHON), 'manage.py', 'migrate', '--noinput'], cwd=API, env=env, check=True)
    with tempfile.TemporaryDirectory(prefix='velora-a6-p1-') as temp:
        fixtures = Path(temp) / 'fixtures.json'
        seed = subprocess.check_output([str(PYTHON), str(ROOT / 'e2e/a6-p1/seed.py')], cwd=ROOT, env=env)
        fd = os.open(fixtures, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(fd, 'wb') as file:
            file.write(seed)
        api_port, web_port = port(), port()
        while web_port == api_port:
            web_port = port()
        api_url, web_url = f'http://127.0.0.1:{api_port}', f'http://127.0.0.1:{web_port}'
        env.update(CORS_ALLOWED_ORIGINS=web_url, A6_P1_E2E_FIXTURES=str(fixtures),
                   A6_P1_E2E_API=api_url + '/api', A6_P1_E2E_WEB=web_url,
                   VITE_API_BASE_URL=api_url + '/api')
        config_path.parent.mkdir(parents=True, exist_ok=True)
        config_path.write_text("import { mergeConfig } from 'vite';\nimport base from '../../vite.config';\n" +
                               f"export default mergeConfig(base, {{ cacheDir: {str(Path(temp) / 'vite-cache')!r}, optimizeDeps: {{ include: ['react-multi-date-picker'] }} }});\n")
        with open(Path(temp) / 'api.log', 'w') as apilog, open(Path(temp) / 'web.log', 'w') as weblog:
            processes.append(subprocess.Popen([str(PYTHON), 'manage.py', 'runserver', f'127.0.0.1:{api_port}', '--noreload'], cwd=API, env=env, stdout=apilog, stderr=subprocess.STDOUT, start_new_session=True))
            processes.append(subprocess.Popen(['pnpm', 'exec', 'vite', '--config', str(config_path), '--host', '127.0.0.1', '--port', str(web_port), '--strictPort'], cwd=ROOT / 'apps/web', env=env, stdout=weblog, stderr=subprocess.STDOUT, start_new_session=True))
            try:
                ready(api_url + '/api/health/', processes[0])
                ready(web_url + '/login', processes[1])
            except RuntimeError:
                apilog.flush(); weblog.flush()
                print((Path(temp) / 'api.log').read_text()[-3000:], file=sys.stderr)
                print((Path(temp) / 'web.log').read_text()[-3000:], file=sys.stderr)
                raise
            result = subprocess.run(['pnpm', 'exec', 'playwright', 'test', '--config=e2e/playwright.a6-p1.config.ts'], cwd=ROOT, env=env)
            sys.exit(result.returncode)
finally:
    for process in processes:
        if process.poll() is None:
            os.killpg(process.pid, signal.SIGTERM)
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                os.killpg(process.pid, signal.SIGKILL)
                process.wait()
    config_path.unlink(missing_ok=True)
    print(f'Isolated database retained for inspection: {name}', flush=True)
