"""Apply project templates to live projects.

Project WBS rows are copy-on-write: editing ProjectTemplateWBS never syncs
into previously applied project trees. force=True is an explicit replace and
must not silently rewrite dependent live data.
"""
from __future__ import annotations

from django.db import transaction

from master_data.models import ProjectMember, ProjectMemberRole, Role
from projects.models import Activity, Project, WBS
from project_templates.models import ProjectTemplate, ProjectTemplateWBS


class TemplateApplyConflict(ValueError):
    """Raised when force-replace cannot safely clear existing project WBS."""

    def __init__(self, message, code='template_force_blocked'):
        super().__init__(message)
        self.code = code


def _project_wbs_has_blocking_dependencies(project: Project) -> str | None:
    """Return a stable conflict code if force-replace must be refused."""
    from cost_control.models import ActualCost, Budget
    from documents.models import ProjectDocument
    from schedule.models import ActivityProgress

    wbs_ids = list(
        WBS.objects.filter(project=project, is_deleted=False).values_list('id', flat=True)
    )
    if not wbs_ids:
        return None
    if Budget.objects.filter(wbs_id__in=wbs_ids, is_deleted=False).exists():
        return 'wbs_has_cost'
    if ActualCost.objects.filter(wbs_id__in=wbs_ids, is_deleted=False).exists():
        return 'wbs_has_cost'
    if ProjectDocument.objects.filter(related_wbs_id__in=wbs_ids, is_deleted=False).exists():
        return 'wbs_has_documents'
    activity_ids = list(
        Activity.objects.filter(project=project, wbs_id__in=wbs_ids, is_deleted=False).values_list(
            'id', flat=True
        )
    )
    if activity_ids and ActivityProgress.objects.filter(activity_id__in=activity_ids).exists():
        return 'wbs_has_progress'
    return None


@transaction.atomic
def apply_template_to_project(
    template: ProjectTemplate,
    project: Project,
    *,
    force: bool = False,
    user=None,
) -> dict:
    has_wbs = WBS.objects.filter(project=project, is_deleted=False).exists()
    if has_wbs and not force:
        raise ValueError('Project already has WBS nodes. Pass force=true to replace.')

    if force and has_wbs:
        conflict = _project_wbs_has_blocking_dependencies(project)
        if conflict:
            raise TemplateApplyConflict(
                f'Cannot force-replace template: existing WBS has dependencies ({conflict}).',
                code=conflict,
            )
        # Soft-delete existing tree (no hard delete) when safe.
        for act in Activity.objects.filter(project=project, is_deleted=False):
            act.soft_delete(user=user)
        for node in WBS.objects.filter(project=project, is_deleted=False).order_by('-depth'):
            node.soft_delete(user=user)

    template_nodes = list(
        ProjectTemplateWBS.objects.filter(template=template)
        .select_related('parent')
        .prefetch_related('activities')
        .order_by('level', 'order', 'wbs_code')
    )

    wbs_map: dict[str, WBS] = {}

    for tnode in template_nodes:
        if tnode.parent_id is None:
            wbs = WBS.add_root(
                project_id=project.id,
                wbs_code=tnode.wbs_code,
                wbs_name=tnode.wbs_name,
                weight_physical=tnode.weight_physical,
            )
        else:
            parent_wbs = wbs_map[str(tnode.parent_id)]
            wbs = parent_wbs.add_child(
                project_id=project.id,
                wbs_code=tnode.wbs_code,
                wbs_name=tnode.wbs_name,
                weight_physical=tnode.weight_physical,
            )
        wbs_map[str(tnode.id)] = wbs

        for tact in tnode.activities.all():
            Activity.objects.create(
                project=project,
                wbs=wbs,
                activity_code=tact.activity_code,
                activity_name=tact.activity_name,
                unit_id=None,
                weight=tact.weight,
                created_by=user,
                updated_by=user,
            )

    roles_added = 0
    for tr in template.template_roles.select_related('role').all():
        for member in ProjectMember.objects.filter(project=project, status='active'):
            if not ProjectMemberRole.objects.filter(member=member, role=tr.role).exists():
                ProjectMemberRole.objects.create(member=member, role=tr.role)
                roles_added += 1

    return {
        'wbs_nodes_created': len(wbs_map),
        # ⚡ Bolt: Use python iteration over prefetched activities collection to avoid N+1 queries from .count()
        'activities_created': sum(len(n.activities.all()) for n in template_nodes),
        'roles_applied': roles_added,
    }


@transaction.atomic
def save_project_as_template(
    project: Project,
    *,
    template_name: str,
    description: str = '',
    project_type: str = 'other',
    created_by=None,
    is_system: bool = False,
) -> ProjectTemplate:
    template = ProjectTemplate.objects.create(
        template_name=template_name,
        description=description,
        project_type=project_type,
        is_system=is_system,
        created_by=created_by,
    )

    wbs_nodes = list(WBS.get_tree(WBS.objects.filter(project_id=project.id)))
    wbs_to_template: dict[str, ProjectTemplateWBS] = {}

    for node in wbs_nodes:
        parent = node.get_parent()
        parent_template = wbs_to_template.get(str(parent.id)) if parent else None
        tnode = ProjectTemplateWBS.objects.create(
            template=template,
            parent=parent_template,
            wbs_code=node.wbs_code,
            wbs_name=node.wbs_name,
            weight_physical=node.weight_physical,
            level=node.depth,
            order=0,
        )
        wbs_to_template[str(node.id)] = tnode

        for act in Activity.objects.filter(wbs=node):
            from project_templates.models import ProjectTemplateActivity

            ProjectTemplateActivity.objects.create(
                template_wbs=tnode,
                activity_code=act.activity_code,
                activity_name=act.activity_name,
                unit=act.unit.unit_symbol if act.unit_id else '',
                weight=act.weight,
            )

    return template
