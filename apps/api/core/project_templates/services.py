"""Apply project templates to live projects."""
from __future__ import annotations

from django.db import transaction

from master_data.models import ProjectMember, ProjectMemberRole, Role
from projects.models import Activity, Project, WBS
from project_templates.models import ProjectTemplate, ProjectTemplateWBS


@transaction.atomic
def apply_template_to_project(
    template: ProjectTemplate,
    project: Project,
    *,
    force: bool = False,
    user=None,
) -> dict:
    if WBS.objects.filter(project=project).exists() and not force:
        raise ValueError('Project already has WBS nodes. Pass force=true to replace.')

    if force:
        Activity.objects.filter(project=project).delete()
        WBS.objects.filter(project=project).delete()

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
        'activities_created': sum(n.activities.count() for n in template_nodes),
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
