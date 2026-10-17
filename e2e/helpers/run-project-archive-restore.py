"""Run validation commands on an explicitly disposable restore database.

Source the repository .env before invoking. This runner never drops a database or
changes .env; it substitutes only the selected database name for the child.
"""
import os
from pathlib import Path
import subprocess
import sys
from urllib.parse import urlsplit, urlunsplit

root = Path(__file__).resolve().parents[2]
name = os.environ.get('RESTORE_VALIDATION_DATABASE', 'velora_restore_validation')
if not name.startswith('velora_restore_') or not name.replace('_', '').isalnum():
    raise SystemExit('RESTORE_VALIDATION_DATABASE must be a disposable velora_restore_* name')
if not os.environ.get('DATABASE_URL') or len(sys.argv) < 2:
    raise SystemExit('Source .env, then provide --create-db or a command to execute')
env = os.environ.copy()
url = urlsplit(env['DATABASE_URL'])
env['DATABASE_URL'] = urlunsplit(url._replace(path='/' + name))
env.update(
    AUDIT_LOG_ASYNC='false', CELERY_TASK_ALWAYS_EAGER='true',
    DJANGO_SETTINGS_MODULE='config.settings', PYTHONPATH=str(root / 'apps/api/core'),
)
if sys.argv[1:] == ['--create-db']:
    import psycopg
    from psycopg import sql
    with psycopg.connect(os.environ['DATABASE_URL'], autocommit=True) as connection:
        exists = connection.execute('SELECT 1 FROM pg_database WHERE datname=%s', (name,)).fetchone()
        if not exists:
            connection.execute(sql.SQL('CREATE DATABASE {}').format(sql.Identifier(name)))
    print('Disposable restore validation database ready; original database unchanged.')
else:
    result = subprocess.run(sys.argv[1:], cwd=root / 'apps/api/core', env=env)
    raise SystemExit(result.returncode)
