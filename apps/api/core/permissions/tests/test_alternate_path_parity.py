"""A6-P4 alternate/legacy path parity probes."""

import pytest
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group
from rest_framework import status
from rest_framework.test import APIClient

User = get_user_model()


@pytest.mark.django_db
def test_visitor_cannot_write_legacy_items():
    visitor = User.objects.create_user(
        username='visitor_items',
        mobile='+989120000301',
        password='x',
    )
    group, _ = Group.objects.get_or_create(name='visitor')
    visitor.groups.add(group)
    client = APIClient()
    client.force_authenticate(user=visitor)
    listed = client.get('/api/items/')
    assert listed.status_code == status.HTTP_200_OK
    created = client.post('/api/items/', {'name': 'blocked'}, format='json')
    assert created.status_code in (status.HTTP_403_FORBIDDEN, status.HTTP_405_METHOD_NOT_ALLOWED)


@pytest.mark.django_db
def test_legacy_items_import_requires_org_catalog_authority():
    from inventory.models import Category

    category = Category.objects.create(name='Cat')

    visitor = User.objects.create_user(
        username='visitor_items_imp',
        mobile='+989120000302',
        password='x',
    )
    g, _ = Group.objects.get_or_create(name='visitor')
    visitor.groups.add(g)
    client = APIClient()
    client.force_authenticate(user=visitor)
    from django.core.files.uploadedfile import SimpleUploadedFile

    denied = client.post(
        '/api/items/import_items/',
        {'file': SimpleUploadedFile('empty.xlsx', b'minimal', content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')},
        format='multipart',
    )
    assert denied.status_code == status.HTTP_403_FORBIDDEN

    admin = User.objects.create_user(
        username='admin_items_imp',
        mobile='+989120000303',
        password='x',
    )
    ga, _ = Group.objects.get_or_create(name='admin')
    admin.groups.add(ga)
    admin_client = APIClient()
    admin_client.force_authenticate(user=admin)
    allowed = admin_client.post(
        '/api/items/',
        {'name': 'legacy item', 'quantity': 1, 'category': category.id},
        format='json',
    )
    assert allowed.status_code == status.HTTP_201_CREATED, allowed.content
