import pytest
from django.contrib.auth.models import Group


def _user_in_group(django_user_model, *, username, mobile, group_name):
    group, _ = Group.objects.get_or_create(name=group_name)
    user = django_user_model.objects.create_user(
        username=username,
        mobile=mobile,
        password='password',
    )
    user.groups.add(group)
    return user


@pytest.fixture
def hr_user(db, django_user_model):
    return _user_in_group(
        django_user_model,
        username='hruser',
        mobile='+989121234569',
        group_name='hr',
    )


@pytest.fixture
def hr_client(api_client, hr_user):
    api_client.force_authenticate(user=hr_user)
    return api_client


@pytest.fixture
def business_setup_user(db, django_user_model):
    return _user_in_group(
        django_user_model,
        username='bizsetup',
        mobile='+989121234570',
        group_name='business-setup',
    )


@pytest.fixture
def business_setup_client(api_client, business_setup_user):
    api_client.force_authenticate(user=business_setup_user)
    return api_client


@pytest.fixture
def staff_user(db, django_user_model):
    return django_user_model.objects.create_user(
        username='staffuser',
        mobile='+989121234571',
        password='password',
        is_staff=True,
    )


@pytest.fixture
def staff_client(api_client, staff_user):
    api_client.force_authenticate(user=staff_user)
    return api_client
