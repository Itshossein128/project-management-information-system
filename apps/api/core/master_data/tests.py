import pytest
from django.db import IntegrityError
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from master_data.models import ProjectMember, ProjectPosition, MemberStatus, WageType
from projects.models import Project

User = get_user_model()

@pytest.fixture
def project(db):
    user = User.objects.create_user(username='pm2', password='pwd')
    return Project.objects.create(
        project_code='PRJ-002',
        project_name='Test Project 2',
        employer='Test Employer 2',
        start_date='2024-01-01'
    )

@pytest.fixture
def test_user(db):
    return User.objects.create_user(username='tester', password='pwd')

@pytest.mark.django_db
class TestMasterDataModels:
    def test_create_project_position(self, project):
        pos = ProjectPosition.objects.create(
            project=project,
            position_name='Site Engineer',
            slug='site_engineer'
        )
        assert pos.id is not None
        assert pos.is_active is True
        assert pos.label == 'Site Engineer'

    def test_project_position_invalid_slug(self, project):
        pos = ProjectPosition(
            project=project,
            position_name='Site Engineer',
            slug='Invalid Slug!'
        )
        with pytest.raises(ValidationError):
            pos.full_clean()

    def test_create_project_member(self, project, test_user):
        member = ProjectMember.objects.create(
            project=project,
            user=test_user,
            status=MemberStatus.ACTIVE,
            wage_type=WageType.MONTHLY
        )
        assert member.id is not None
        assert member.status == MemberStatus.ACTIVE
        assert member.wage_type == WageType.MONTHLY

    def test_project_member_unique_constraint(self, project, test_user):
        ProjectMember.objects.create(
            project=project,
            user=test_user
        )
        with pytest.raises(IntegrityError):
            ProjectMember.objects.create(
                project=project,
                user=test_user
            )
