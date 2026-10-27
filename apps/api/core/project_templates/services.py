"""Apply project templates to live projects.

Project WBS rows are copy-on-write: editing ProjectTemplateWBS never syncs
into previously applied project trees. force=True is an explicit replace and
must not silently rewrite dependent live data.
"""
from __future__ import annotations

from django.db import transaction

from master_data.models import ProjectMember, ProjectMemberRole, Role
from projects.models import Activity, Project, WBS
from project_templates.models import (
    LaborTitleCatalog,
    ProjectReportingConfiguration,
    ProjectTemplate,
    ProjectTemplateWBS,
)


# Feature 033 (data-model §1.2): default controlled stoppage-reason vocabulary.
# Codes are stable and language-independent; labels are translatable and seeded
# into every activation snapshot. Template-level extension rows, when present,
# are appended after the defaults.
DEFAULT_STOPPAGE_REASONS = (
    ('breakdown', 'Breakdown', 'خرابی تجهیزات'),
    ('lack_of_fuel', 'Lack of fuel', 'کمبود سوخت'),
    ('weather', 'Weather', 'شرایط جوی نامساعد'),
    ('no_operator', 'No operator', 'عدم تخصیص اپراتور'),
    ('site_obstruction', 'Site obstruction', 'بازداشت کارگاه'),
)


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


class ReportingConfigurationConflict(ValueError):
    """Raised when an activation date conflicts with an existing configuration."""

    def __init__(self, message, code='reporting_configuration_date_conflict'):
        super().__init__(message)
        self.code = code


@transaction.atomic
def activate_project_reporting_configuration(
    project: Project,
    template: ProjectTemplate,
    effective_from,
    user=None,
    confirm_backdated: bool = False,
    reason: str = '',
):
    from project_templates.models import (
        ProjectReportingConfiguration,
        ProjectReportingConfigurationLaborTitle,
        ProjectReportingConfigurationStoppageReason,
        ProjectReportingConfigurationUnit,
    )

    # 1. Exact date conflict check
    if ProjectReportingConfiguration.objects.filter(
        project=project, effective_from=effective_from,
    ).exists():
        raise ReportingConfigurationConflict(
            f'A reporting configuration is already active for {effective_from}.',
            code='reporting_configuration_date_conflict',
        )

    # 2. Append-only check: cannot be earlier than or equal to latest without explicit confirmation
    latest = (
        ProjectReportingConfiguration.objects.filter(project=project)
        .order_by('-effective_from')
        .first()
    )
    if latest and effective_from <= latest.effective_from and not confirm_backdated:
        raise ReportingConfigurationConflict(
            'Activating a backdated configuration requires explicit confirmation.',
            code='backdated_activation_requires_confirmation',
        )

    # 3. Find supersedes: latest prior configuration
    supersedes = (
        ProjectReportingConfiguration.objects.filter(
            project=project, effective_from__lt=effective_from,
        )
        .order_by('-effective_from')
        .first()
    )

    # 4. Create immutable configuration snapshot
    config = ProjectReportingConfiguration.objects.create(
        project=project,
        source_template=template,
        source_template_name_snapshot=template.template_name,
        effective_from=effective_from,
        activated_by=user,
        supersedes=supersedes,
    )

    # 5. Snapshot required units from template
    template_units = list(template.required_units.all().order_by('display_order', 'id'))
    for order, tu in enumerate(template_units):
        ProjectReportingConfigurationUnit.objects.create(
            configuration=config,
            unit=tu.unit,
            display_order=order,
        )

    # 6. Feature 033 (data-model §1.1/§1.2): immutable snapshot of the labor-title
    # catalog, the man-hours rule, and the controlled stoppage vocabulary. Only the
    # latest catalog version of the template becomes effective at activation.
    latest_catalog = (
        LaborTitleCatalog.objects.filter(template=template)
        .order_by('-created_at')
        .first()
    )
    if latest_catalog is None:
        from project_templates.labor_catalog_seeds import (
            seed_default_catalogs_for_owner,
            seed_default_catalogs_for_template,
        )

        if template is not None:
            latest_catalog = seed_default_catalogs_for_template(template)
        else:
            latest_catalog = seed_default_catalogs_for_owner()

    if latest_catalog is not None:
        for title in latest_catalog.titles.filter(active=True).order_by('display_order', 'id'):
            ProjectReportingConfigurationLaborTitle.objects.create(
                configuration=config,
                title_code=title.title_code,
                title_label=title.title_label,
                title_label_fa=title.title_label_fa,
                category=title.category,
                display_order=title.display_order,
                legacy_alias=title.legacy_alias,
                source_catalog_version=latest_catalog.version_name,
            )

    # Man-hours rule: only one code exists in the fixed registry today; the
    # snapshot carries it plus the template-independent default shift length.
    if not config.man_hours_rule_code:
        config.man_hours_rule_code = 'standard_shift_plus_overtime'
    if config.standard_shift_hours is None:
        config.standard_shift_hours = 8
    config.save(update_fields=['man_hours_rule_code', 'standard_shift_hours'])

    for ordinal, (code, label_en, label_fa) in enumerate(DEFAULT_STOPPAGE_REASONS):
        ProjectReportingConfigurationStoppageReason.objects.create(
            configuration=config,
            reason_code=code,
            reason_label=label_en,
            reason_label_fa=label_fa,
            display_order=ordinal,
        )

    return config


def preview_project_reporting_configuration(
    project: Project,
    template: ProjectTemplate,
    effective_from,
) -> dict:
    from field_reports.models import DailyReport
    from project_templates.models import ProjectReportingConfiguration

    latest = (
        ProjectReportingConfiguration.objects.filter(project=project)
        .order_by('-effective_from')
        .first()
    )
    is_backdated = bool(latest and effective_from <= latest.effective_from)
    affected_count = DailyReport.objects.filter(
        project=project,
        report_date__gte=effective_from,
        is_deleted=False,
    ).count()

    # Feature 033 (contract §2): preview shows the exact labor catalog snapshot,
    # man-hours rule and stoppage vocabulary that would become effective.
    from project_templates.models import LaborTitleCatalog

    catalog = (
        LaborTitleCatalog.objects.filter(template=template)
        .order_by('-created_at')
        .first()
    )
    labor_titles = [
        {
            'title_code': t.title_code,
            'title_label': t.title_label,
            'title_label_fa': t.title_label_fa,
            'category': t.category,
            'display_order': t.display_order,
            'legacy_alias': t.legacy_alias,
            'project_specific': t.project_specific,
            'source_catalog_version': catalog.version_name if catalog else '',
        }
        for t in (catalog.titles.order_by('display_order', 'id') if catalog else [])
    ]

    return {
        'template_id': str(template.id),
        'template_name': template.template_name,
        'effective_from': str(effective_from),
        'required_units': [
            u.unit for u in template.required_units.all().order_by('display_order', 'id')
        ],
        'labor_titles': labor_titles,
        'man_hours_rule': {
            'rule_code': ProjectReportingConfiguration._meta.get_field(
                'man_hours_rule_code'
            ).get_default(),
            'parameters': {
                'standard_shift_hours': str(
                    ProjectReportingConfiguration._meta.get_field(
                        'standard_shift_hours'
                    ).get_default()
                ),
            },
        },
        'stoppage_reasons': [
            {'reason_code': c, 'reason_label': en, 'reason_label_fa': fa}
            for c, en, fa in DEFAULT_STOPPAGE_REASONS
        ],
        'is_backdated': is_backdated,
        'affected_reports_count': affected_count,
        'latest_effective_from': str(latest.effective_from) if latest else None,
    }


# ---------------------------------------------------------------------------
# Labor-title catalog draft CRUD (feature 033, contract §1)
# ---------------------------------------------------------------------------


def create_labor_catalog(template: ProjectTemplate, *, version_name: str, notes: str = '', titles: list | None = None) -> LaborTitleCatalog:
    from django.core.exceptions import ValidationError as DjangoValidationError

    from project_templates.models import LaborTitleCatalogTitle

    with transaction.atomic():
        catalog = LaborTitleCatalog.objects.create(
            template=template, version_name=version_name, notes=notes,
        )
        for row in titles or []:
            payload = {
                k: row[k]
                for k in (
                    'title_code', 'title_label', 'title_label_fa', 'category',
                    'display_order', 'active', 'legacy_alias', 'project_specific',
                )
                if k in row and row[k] is not None
            }
            payload.setdefault('display_order', 0)
            payload.setdefault('legacy_alias', '')
            payload.setdefault('active', True)
            payload.setdefault('project_specific', False)
            try:
                LaborTitleCatalogTitle.objects.create(catalog=catalog, **payload)
            except DjangoValidationError as exc:
                raise _catalog_payload_error(exc)
        return catalog


def _catalog_payload_error(exc) -> ValueError:
    message = getattr(exc, 'message', str(exc))
    text = message if isinstance(message, str) else '; '.join(map(str, message))
    if 'title_code' in text:
        code = 'duplicate_title_code'
    elif 'display_order' in text:
        code = 'duplicate_display_order'
    else:
        code = 'invalid_catalog_title'
    return ValueError(f'{code}: {text}')


def update_labor_catalog(catalog: LaborTitleCatalog, *, version_name: str | None = None, notes: str | None = None) -> LaborTitleCatalog:
    if version_name is not None:
        catalog.version_name = version_name
    if notes is not None:
        catalog.notes = notes
    catalog.save(update_fields=['version_name', 'notes', 'updated_at'])
    return catalog


# ---------------------------------------------------------------------------
# Labor-title resolution (feature 033, contract reporting-configuration-catalog-api.md §3)
# ---------------------------------------------------------------------------


def resolve_labor_title(configuration: ProjectReportingConfiguration, job_title: str):
    """Resolve a unit-report job title against the effective snapshot.

    Resolution order (contract §3): legacy alias → exact label (standard
    stored label, locale-independent) → project-specific title (or stable
    title_code). Returns the matching snapshot title row or ``None``
    (callers reject with ``unknown_job_title``).
    """
    if configuration is None or not (job_title or '').strip():
        return None
    needle = job_title.strip().lower()

    from project_templates.models import (
        LaborTitleCatalogTitle,
        ProjectReportingConfigurationLaborTitle,
    )

    titles = list(
        ProjectReportingConfigurationLaborTitle.objects.filter(
            configuration=configuration,
        ).order_by('display_order', 'title_code')
    )
    if not titles:
        from project_templates.labor_catalog_seeds import (
            seed_default_catalogs_for_owner,
            seed_default_catalogs_for_template,
        )

        template = getattr(configuration, 'source_template', None)
        latest_catalog = None
        if template is not None:
            latest_catalog = (
                LaborTitleCatalog.objects.filter(template=template)
                .order_by('-created_at')
                .first()
            )
            if latest_catalog is None:
                latest_catalog = seed_default_catalogs_for_template(template)
        if latest_catalog is None:
            latest_catalog = seed_default_catalogs_for_owner()

        if latest_catalog:
            for t in latest_catalog.titles.filter(active=True).order_by('display_order', 'id'):
                ProjectReportingConfigurationLaborTitle.objects.create(
                    configuration=configuration,
                    title_code=t.title_code,
                    title_label=t.title_label,
                    title_label_fa=t.title_label_fa,
                    category=t.category,
                    display_order=t.display_order,
                    legacy_alias=t.legacy_alias,
                    source_catalog_version=latest_catalog.version_name,
                )
            titles = list(
                ProjectReportingConfigurationLaborTitle.objects.filter(
                    configuration=configuration,
                ).order_by('display_order', 'title_code')
            )
    if not titles:
        return None

    # Determine which title_codes in this snapshot came from project_specific=True
    project_specific_codes: set[str] = set()
    if configuration.source_template_id:
        project_specific_codes = set(
            LaborTitleCatalogTitle.objects.filter(
                catalog__template_id=configuration.source_template_id,
                project_specific=True,
                title_code__in=[t.title_code for t in titles],
            ).values_list('title_code', flat=True)
        )

    # 1) legacy alias first: keeps historical rows' original evidence meaningful
    for title in titles:
        if title.legacy_alias:
            aliases = [a.strip().lower() for a in title.legacy_alias.split(',')]
            if needle in aliases:
                return title
    # 2) exact label match on standard (non-project-specific) titles
    for title in titles:
        if title.title_code in project_specific_codes:
            continue
        if title.title_label and title.title_label.strip().lower() == needle:
            return title
        if title.title_label_fa and title.title_label_fa.strip().lower() == needle:
            return title
    # 3) project-specific title match (by label or code) + stable code match
    for title in titles:
        if title.title_code in project_specific_codes:
            if title.title_label and title.title_label.strip().lower() == needle:
                return title
            if title.title_label_fa and title.title_label_fa.strip().lower() == needle:
                return title
            if title.title_code and title.title_code.strip().lower() == needle:
                return title
    for title in titles:
        if title.title_code and title.title_code.strip().lower() == needle:
            return title
    return None


def resolve_stoppage_reason(configuration, reason_code: str):
    """Resolve a stoppage reason code against the effective configuration snapshot."""
    if configuration is None or not (reason_code or '').strip():
        return None
    from project_templates.models import ProjectReportingConfigurationStoppageReason

    return ProjectReportingConfigurationStoppageReason.objects.filter(
        configuration=configuration,
        reason_code=reason_code.strip(),
    ).first()

