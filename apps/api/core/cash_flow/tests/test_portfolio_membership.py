import pytest

from cash_flow.services.portfolio_access import projects_visible_for_cashflow
from master_data.models import MemberStatus, ProjectMember, ProjectMemberRole


@pytest.mark.django_db
def test_user_without_membership_does_not_see_other_project(
    user, project, second_project, outsider_user, project_manager_role
):
    # outsider is member only of `project`, not second_project
    m = ProjectMember.objects.create(
        project=project,
        user=outsider_user,
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=m, role=project_manager_role)

    visible = list(projects_visible_for_cashflow(outsider_user).values_list('id', flat=True))
    assert project.id in visible
    assert second_project.id not in visible


@pytest.mark.django_db
def test_creator_with_pm_sees_own_project(user, project):
    visible = list(projects_visible_for_cashflow(user).values_list('id', flat=True))
    assert project.id in visible
