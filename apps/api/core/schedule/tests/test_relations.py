import pytest

from projects.models import Activity, ActivityRelation, RelationType
from schedule.services.cycle_detection import would_create_cycle
from wbs.services import create_wbs_node


@pytest.mark.django_db
class TestCycleDetection:
    def test_direct_cycle(self, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        a = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A1',
            activity_name='A',
            created_by=user,
            updated_by=user,
        )
        b = Activity.objects.create(
            project=project,
            wbs=wbs,
            activity_code='A2',
            activity_name='B',
            created_by=user,
            updated_by=user,
        )
        assert would_create_cycle(project.id, a.id, a.id) is True
        assert would_create_cycle(project.id, a.id, b.id) is False

    def test_indirect_cycle(self, project, user):
        wbs, _ = create_wbs_node(project_id=project.id, wbs_code='1', wbs_name='Root')
        a = Activity.objects.create(
            project=project, wbs=wbs, activity_code='A1', activity_name='A',
            created_by=user, updated_by=user,
        )
        b = Activity.objects.create(
            project=project, wbs=wbs, activity_code='A2', activity_name='B',
            created_by=user, updated_by=user,
        )
        c = Activity.objects.create(
            project=project, wbs=wbs, activity_code='A3', activity_name='C',
            created_by=user, updated_by=user,
        )
        ActivityRelation.objects.create(
            predecessor=a, successor=b, created_by=user, updated_by=user,
        )
        ActivityRelation.objects.create(
            predecessor=b, successor=c, created_by=user, updated_by=user,
        )
        assert would_create_cycle(project.id, c.id, a.id) is True
