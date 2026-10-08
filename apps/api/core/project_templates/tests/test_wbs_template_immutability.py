from decimal import Decimal

import pytest

from cost_control.models import Budget, CostCategory
from projects.models import WBS
from project_templates.models import ProjectTemplate, ProjectTemplateWBS, ProjectType
from project_templates.services import apply_template_to_project


@pytest.fixture
def wbs_template(db, user):
    tpl = ProjectTemplate.objects.create(
        template_name='Road base',
        project_type=ProjectType.ROAD,
        created_by=user,
    )
    ProjectTemplateWBS.objects.create(
        template=tpl,
        parent=None,
        wbs_code='1',
        wbs_name='Root Template',
        level=1,
        order=0,
    )
    return tpl


@pytest.mark.django_db
def test_template_edit_does_not_change_applied_project(project, user, wbs_template):
    result = apply_template_to_project(wbs_template, project, user=user)
    assert result['wbs_nodes_created'] == 1
    project_node = WBS.objects.get(project=project, is_deleted=False)
    assert project_node.wbs_name == 'Root Template'

    tnode = wbs_template.wbs_nodes.get()
    tnode.wbs_name = 'CHANGED TEMPLATE'
    tnode.wbs_code = '99'
    tnode.save()

    project_node.refresh_from_db()
    assert project_node.wbs_name == 'Root Template'
    assert project_node.wbs_code != '99'


@pytest.mark.django_db
def test_force_apply_blocked_when_cost_depends(project, user, wbs_template):
    apply_template_to_project(wbs_template, project, user=user)
    node = WBS.objects.get(project=project, is_deleted=False)
    Budget.objects.create(
        project=project,
        wbs=node,
        cost_category=CostCategory.LABOR,
        budget_amount=Decimal('500'),
        created_by=user,
        updated_by=user,
    )
    with pytest.raises(Exception) as exc:
        apply_template_to_project(wbs_template, project, force=True, user=user)
    blob = str(exc.value).lower()
    assert 'depend' in blob or 'cost' in blob or 'wbs_has' in blob or 'force' in blob
