from unittest.mock import MagicMock

import pytest
from django.db import OperationalError
from redis.exceptions import ConnectionError as RedisConnectionError

from common import health as health_module


@pytest.fixture
def dependencies(monkeypatch):
    connection = MagicMock()
    cache = MagicMock()
    monkeypatch.setattr(health_module, 'connection', connection)
    monkeypatch.setattr(health_module, 'cache', cache)
    return connection, cache


def test_health_checks_database_and_cache_without_authentication(client, dependencies):
    connection, cache = dependencies
    response = client.get('/api/health/')
    assert response.status_code == 200
    assert response.json() == {'status': 'ok'}
    connection.cursor.return_value.__enter__.return_value.execute.assert_called_once_with('SELECT 1')
    cache.get.assert_called_once_with('velora:health')


@pytest.mark.parametrize('dependency', ['database', 'cache'])
def test_health_returns_unavailable_when_a_dependency_fails(client, dependencies, dependency):
    connection, cache = dependencies
    if dependency == 'database':
        connection.cursor.side_effect = OperationalError('private database details')
    else:
        cache.get.side_effect = RedisConnectionError('private cache details')
    response = client.get('/api/health/')
    assert response.status_code == 503
    assert response.json() == {'status': 'unavailable'}


def test_health_only_accepts_get(client, dependencies):
    response = client.post('/api/health/')
    assert response.status_code == 405
