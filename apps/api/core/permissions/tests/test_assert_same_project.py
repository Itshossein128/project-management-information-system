"""A6-P4 cross-project relation guard."""

import pytest
from django.contrib.auth import get_user_model

from config.exceptions import CodedValidationError
from permissions.project import assert_same_project

User = get_user_model()


@pytest.mark.django_db
def test_assert_same_project_allows_matching_ids():
    assert_same_project('a', 'a')
    assert_same_project('a', None)


@pytest.mark.django_db
def test_assert_same_project_fails_closed_when_request_missing():
    with pytest.raises(CodedValidationError) as exc:
        assert_same_project(None, 'a')
    assert exc.value.default_code == 'project_scope_mismatch'


@pytest.mark.django_db
def test_assert_same_project_rejects_mismatch():
    with pytest.raises(CodedValidationError) as exc:
        assert_same_project('project-a', 'project-b')
    assert exc.value.default_code == 'project_scope_mismatch'
