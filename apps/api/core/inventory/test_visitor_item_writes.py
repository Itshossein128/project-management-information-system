"""Organization visitors cannot write the legacy item catalog."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

from inventory.models import Category, Item

User = get_user_model()


@pytest.fixture
def visitor(db):
    user = User.objects.create_user(
        username='visitor',
        mobile='+989121110001',
        full_name='Visitor',
        password='testpass123',
    )
    group, _created = Group.objects.get_or_create(name='visitor')
    user.groups.add(group)
    return user


@pytest.fixture
def category(db):
    return Category.objects.create(name='Steel')


@pytest.mark.django_db
def test_visitor_can_read_items_but_cannot_write(visitor, category):
    client = APIClient()
    client.force_authenticate(user=visitor)
    assert client.get('/api/items/').status_code == status.HTTP_200_OK

    created = client.post(
        '/api/items/',
        {'name': 'Bolt', 'quantity': 2, 'category': category.id},
        format='json',
    )
    assert created.status_code == status.HTTP_403_FORBIDDEN
    assert not Item.objects.filter(name='Bolt').exists()

    imported = client.post('/api/items/import_items/', {})
    assert imported.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_org_catalog_writer_can_create_item_and_project_manager_cannot(auth_client, category):
    """Org item writes belong to an account administrator, not every signed-in user."""
    manager = auth_client.post(
        '/api/items/',
        {'name': 'Nut', 'quantity': 4, 'category': category.id},
        format='json',
    )
    assert manager.status_code == status.HTTP_403_FORBIDDEN
    assert not Item.objects.filter(name='Nut').exists()

    writer = User.objects.create_user(
        username='catalog-writer',
        mobile='+989121110099',
        full_name='Catalog Writer',
        password='testpass123',
    )
    group, _created = Group.objects.get_or_create(name='hr')
    writer.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=writer)
    created = client.post(
        '/api/items/',
        {'name': 'Nut', 'quantity': 4, 'category': category.id},
        format='json',
    )
    assert created.status_code == status.HTTP_201_CREATED
    assert Item.objects.filter(name='Nut').exists()
