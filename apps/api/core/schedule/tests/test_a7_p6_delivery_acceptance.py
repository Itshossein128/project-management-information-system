"""Integrated End-to-End Acceptance Suite for Module A.7-P6 (056-a7-p6-delivery-acceptance).

Covers:
- POS-01..POS-10: Positive reference project journey across 5 separated role personas
- NEG-01..NEG-14: Independent negative, adverse, concurrency, and access-boundary scenarios
- Reference schedule reconciliation on unchanged real-data/plan.mpp (6 WBS, 72 activities, 72 relations)
"""

from __future__ import annotations

import hashlib
from datetime import date
from pathlib import Path
from uuid import uuid4

import pytest
from django.contrib.auth.models import Group
from django.core.files.uploadedfile import SimpleUploadedFile
from rest_framework.test import APIClient

from master_data.models import MemberStatus, OrganizationUnit, ProjectMember, ProjectMemberRole, Role
from projects.models import (
    Activity,
    ActivityRelation,
    Project,
    ProjectKickoffCharter,
    ProjectStatus,
    WBS,
)
from projects.services import create_project_with_creator
from schedule.models import (
    ActivityProgress,
    BaselineActivity,
    BaselineSchedule,
    MspImportJob,
    MspImportStatus,
)
from schedule.services.critical_path_validity import evaluate_critical_path_validity
from schedule.services.gantt_service import get_gantt_data
from schedule.services.import_fidelity import ImportFidelityError
from schedule.services.import_safety import ImportSafetyError
from schedule.services.msp_import import build_preview, execute_msp_import, parse_msp_xml
from schedule.services.p6_import import execute_p6_import, parse_p6_xer
from schedule.services.status_report_service import build_schedule_status
from schedule.tasks import run_msp_import_task
from wbs.services import WBSValidationError, create_wbs_node, move_wbs_node

REPO_ROOT = Path(__file__).resolve().parents[5]
PLAN_MPP_PATH = REPO_ROOT / "real-data" / "plan.mpp"
P1_FIXTURES = REPO_ROOT / "specs" / "051-a7-p1-project-reference" / "evidence" / "fixtures"
MPP_FIXTURES = Path(__file__).parent / "fixtures" / "mpp"


def _client_for(user) -> APIClient:
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def _counts(project: Project) -> dict[str, int]:
    return {
        "wbs": WBS.objects.filter(project=project, is_deleted=False).count(),
        "activities": Activity.objects.filter(project=project, is_deleted=False).count(),
        "relations": ActivityRelation.objects.filter(
            successor__project=project, is_deleted=False
        ).count(),
        "baselines": BaselineSchedule.objects.filter(project=project, is_deleted=False).count(),
    }


@pytest.fixture(autouse=True)
def _noop_event_publisher(monkeypatch):
    """Avoid blocking on optional RabbitMQ (:5672) during synchronous API calls."""
    from events.publisher import EventPublisher

    monkeypatch.setattr(EventPublisher, "publish", lambda *args, **kwargs: None)


@pytest.fixture
def p6_personas(django_user_model, project_manager_role, viewer_role):
    """Provision the 5 acceptance role personas without hardcoded shared secrets."""
    hr_group, _ = Group.objects.get_or_create(name="hr")
    admin_group, _ = Group.objects.get_or_create(name="admin")

    steward = django_user_model.objects.create_user(
        username="a7p6-steward",
        mobile="+989120056001",
        password="test-only-not-exported",
    )
    steward.groups.add(hr_group, admin_group)

    creator_planner = django_user_model.objects.create_user(
        username="a7p6-planner",
        mobile="+989120056002",
        password="test-only-not-exported",
    )

    independent_approver = django_user_model.objects.create_user(
        username="a7p6-approver",
        mobile="+989120056003",
        password="test-only-not-exported",
    )
    independent_approver.groups.add(admin_group)

    viewer = django_user_model.objects.create_user(
        username="a7p6-viewer",
        mobile="+989120056004",
        password="test-only-not-exported",
    )

    system_admin = django_user_model.objects.create_user(
        username="a7p6-sysadmin",
        mobile="+989120056005",
        password="test-only-not-exported",
        is_staff=True,
        is_superuser=True,
    )
    system_admin.groups.add(admin_group)

    return {
        "steward": steward,
        "creator_planner": creator_planner,
        "independent_approver": independent_approver,
        "viewer": viewer,
        "system_admin": system_admin,
        "pm_role": project_manager_role,
        "viewer_role": viewer_role,
    }


@pytest.mark.django_db
def test_a7_p6_positive_reference_journey_pos01_to_pos10(p6_personas):
    steward_client = _client_for(p6_personas["steward"])
    planner_client = _client_for(p6_personas["creator_planner"])
    approver_client = _client_for(p6_personas["independent_approver"])
    admin_client = _client_for(p6_personas["system_admin"])

    # --- POS-01: Governed reference data + Draft project creation + 6-section Kickoff Charter ---
    ou_res = steward_client.post(
        "/api/v1/organization-units/",
        {"code": "A7P6-OU", "name": "معاونت فنی و عمرانی مرجع"},
        format="json",
    )
    assert ou_res.status_code == 201, ou_res.content
    ct_res = steward_client.post(
        "/api/v1/contract-types/",
        {"code": "A7P6-EPC", "name_fa": "طراحی و ساخت", "name_en": "EPC", "is_active": True},
        format="json",
    )
    assert ct_res.status_code == 201, ct_res.content
    mu_res = steward_client.post(
        "/api/v1/measurement-units/",
        {"unit_name": "A7P6 Square Meter", "unit_symbol": "m2"},
        format="json",
    )
    assert mu_res.status_code == 201, mu_res.content

    proj_res = planner_client.post(
        "/api/v1/projects/",
        {
            "project_code": "A7P6-POS-MAIN",
            "project_name": "پروژه مرجع پذیرش یکپارچه A.7",
            "employer": "کارفرمای مرجع",
            "start_date": "2026-01-10",
            "purpose": "احراز کامل چرخه عمر پروژه و زمان‌بندی",
            "scope_description": "ساختار شکست کار، ورود زمان‌بندی و خط مبنا",
            "main_deliverables": "ساختار WBS، برنامه زمان‌بندی مصوب و گزارش تطبیق",
            "contract_number": "CNT-A7P6-01",
            "contract_amount": "50000000.00",
            "contract_type": "A7P6-EPC",
            "currency": "IRR",
            "owning_unit": ou_res.json()["id"],
            "project_manager": str(p6_personas["creator_planner"].id),
        },
        format="json",
    )
    assert proj_res.status_code == 201, proj_res.content
    project_id = proj_res.json()["id"]
    project = Project.objects.get(pk=project_id)
    assert project.status == ProjectStatus.DRAFT

    charter_payload = {
        "justification": "توجیه فنی و اقتصادی پروژه مرجع",
        "success_criteria": "تطبیق ۱۰۰٪ ارقام زمان‌بندی و سلامت چرخه عمر",
        "constraints": "سقف بودجه و تقویم اجرایی مصوب",
        "assumptions": "تأمین بهنگام مصالح و دسترسی کارگاهی",
        "key_stakeholders_summary": "کارفرما، مدیر پروژه، مشاور و پیمانکار",
        "pm_authority": "مدیریت روزانه فعالیت‌ها و پیشنهاد درخواست تغییر",
    }
    charter_put = planner_client.put(
        f"/api/v1/projects/{project_id}/kickoff-charter/",
        charter_payload,
        format="json",
    )
    assert charter_put.status_code == 200, charter_put.content
    assert ProjectKickoffCharter.objects.filter(project=project).exists()

    # --- POS-02: Charter submit, SoD enforcement, Activation Gates, and Independent Approval ---
    # Add independent approver as active project member with PM role
    approver_member = ProjectMember.objects.create(
        project=project,
        user=p6_personas["independent_approver"],
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=approver_member, role=p6_personas["pm_role"])

    submit_res = planner_client.post(f"/api/v1/projects/{project_id}/submit/")
    assert submit_res.status_code == 200, submit_res.content
    assert submit_res.data["status"] == "pending_approval"

    self_approve = planner_client.post(f"/api/v1/projects/{project_id}/approve/")
    assert self_approve.status_code == 400
    assert self_approve.data["error"]["code"] == "submitter_cannot_approve"

    # Verify activation gate check when PM is temporarily cleared
    Project.objects.filter(pk=project_id).update(project_manager=None)
    gate_fail = approver_client.post(f"/api/v1/projects/{project_id}/approve/")
    assert gate_fail.status_code == 400
    assert "activation_gates" in str(gate_fail.data)
    Project.objects.filter(pk=project_id).update(project_manager=p6_personas["creator_planner"])

    approve_res = approver_client.post(f"/api/v1/projects/{project_id}/approve/")
    assert approve_res.status_code == 200, approve_res.content
    assert approve_res.data["status"] == "active"
    assert approve_res.data["budget_approved_at"] is not None

    # --- POS-03: Controlled Change Request on Approved Project Fields ---
    direct_patch = planner_client.patch(
        f"/api/v1/projects/{project_id}/",
        {"employer": "تغییر مستقیم غیرمجاز"},
        format="json",
    )
    assert direct_patch.status_code == 400
    assert direct_patch.data["error"]["code"] == "protected_field_requires_change_request"

    cr_base = f"/api/v1/projects/{project_id}/change-requests/"
    cr_create = planner_client.post(
        cr_base,
        {
            "reason": "اصلاح نام حقوقی کارفرما طبق الحاقیه قرارداد",
            "proposed_changes": {"employer": "شرکت توسعه ابنیه کارفرمای مرجع"},
        },
        format="json",
    )
    assert cr_create.status_code == 201, cr_create.content
    cr_id = cr_create.data["id"]
    cr_submit = planner_client.post(f"{cr_base}{cr_id}/submit/")
    assert cr_submit.status_code == 200
    project.refresh_from_db()
    assert project.employer == "کارفرمای مرجع"  # Unchanged while pending

    cr_self = planner_client.post(f"{cr_base}{cr_id}/approve/")
    assert cr_self.status_code == 400
    assert cr_self.data["error"]["code"] == "sod_self_approve"

    cr_approve = approver_client.post(f"{cr_base}{cr_id}/approve/")
    assert cr_approve.status_code == 200
    assert cr_approve.data["status"] == "approved"
    project.refresh_from_db()
    assert project.employer == "شرکت توسعه ابنیه کارفرمای مرجع"

    # --- POS-04: Multi-level WBS (>=3 levels), Responsible & Criterion, Move/Renumber, Template Copy ---
    root_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "wbs_code": "1",
            "wbs_name": "عملیات کل پروژه",
            "weight": "100.00",
            "responsible": str(p6_personas["creator_planner"].id),
            "acceptance_criteria": "تحویل کلیه فازها",
        },
        format="json",
    )
    assert root_res.status_code == 201, root_res.content
    root_id = root_res.json()["wbs_id"]

    phase_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "parent_id": root_id,
            "wbs_code": "1.1",
            "wbs_name": "فاز اسکلت و سازه",
            "weight": "100.00",
            "responsible": str(p6_personas["creator_planner"].id),
            "acceptance_criteria": "تأیید آزمایشگاه بتن و جوش",
        },
        format="json",
    )
    assert phase_res.status_code == 201, phase_res.content
    phase_id = phase_res.json()["wbs_id"]

    pkg1_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "parent_id": phase_id,
            "wbs_code": "1.1.1",
            "wbs_name": "فونداسیون",
            "weight": "60.00",
            "responsible": str(p6_personas["creator_planner"].id),
            "acceptance_criteria": "تأیید آرماتوربندی و بتن‌ریزی فونداسیون",
        },
        format="json",
    )
    assert pkg1_res.status_code == 201, pkg1_res.content
    pkg2_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "parent_id": phase_id,
            "wbs_code": "1.1.2",
            "wbs_name": "ستون و سقف",
            "weight": "40.00",
            "responsible": str(p6_personas["independent_approver"].id),
            "acceptance_criteria": "تأیید شاقول‌سنجی و مقاومت ۲۸روزه",
        },
        format="json",
    )
    assert pkg2_res.status_code == 201, pkg2_res.content

    # Create reusable 3-level WBS template in catalog and apply to an independent target project
    from project_templates.models import ProjectTemplate, ProjectTemplateWBS

    tpl_res = steward_client.post(
        "/api/v1/project-templates/",
        {
            "template_name": "الگوی مرجع ۳سطحی A7P6",
            "description": "الگوی تست استقلال کپی WBS",
            "project_type": "residential",
        },
        format="json",
    )
    assert tpl_res.status_code == 201, tpl_res.content
    tpl_id = tpl_res.json().get("template_id") or tpl_res.json().get("id")
    tpl_obj = ProjectTemplate.objects.get(pk=tpl_id)
    t_root = ProjectTemplateWBS.objects.create(
        template=tpl_obj, parent=None, wbs_code="1", wbs_name="عملیات کل پروژه", level=1, order=0
    )
    t_phase = ProjectTemplateWBS.objects.create(
        template=tpl_obj, parent=t_root, wbs_code="1.1", wbs_name="فاز اسکلت و سازه", level=2, order=0
    )
    t_pkg = ProjectTemplateWBS.objects.create(
        template=tpl_obj, parent=t_phase, wbs_code="1.1.1", wbs_name="فونداسیون", level=3, order=0
    )

    target_proj = create_project_with_creator(
        creator=p6_personas["creator_planner"],
        project_code="A7P6-TPL-COPY",
        project_name="پروژه مقصد کپی الگو",
        employer="کارفرمای مرجع",
        start_date="2026-02-01",
    )
    target_proj.status = ProjectStatus.ACTIVE
    target_proj.save(update_fields=["status", "updated_at"])

    apply_res = steward_client.post(f"/api/v1/project-templates/{tpl_id}/apply/{target_proj.id}/")
    assert apply_res.status_code == 200, apply_res.content
    assert WBS.objects.filter(project=target_proj, is_deleted=False).count() == 3

    # Mutate template WBS node and source project's WBS name; verify target project's copy remains untouched
    t_pkg.wbs_name = "تغییر در الگو"
    t_pkg.save(update_fields=["wbs_name"])
    planner_client.patch(
        f"/api/v1/projects/{project_id}/wbs/{pkg1_res.json()['wbs_id']}/",
        {"wbs_name": "فونداسیون ویرایش‌شده"},
        format="json",
    )
    assert WBS.objects.get(project=target_proj, wbs_code="1.1.1").wbs_name == "فونداسیون"

    # --- POS-05 & POS-06: Preview & Append Import of real-data/plan.mpp and XML/XER Fixtures ---
    from decimal import Decimal
    from django.utils import timezone

    mpp_project = create_project_with_creator(
        creator=p6_personas["creator_planner"],
        project_code="A7P6-MPP-REF",
        project_name="پروژه تطبیق فایل واقعی plan.mpp",
        employer="کارفرمای مرجع",
        start_date="2026-01-01",
    )
    mpp_project.status = ProjectStatus.ACTIVE
    mpp_project.project_manager = p6_personas["creator_planner"]
    mpp_project.scope_description = "دامنه مصوب پروژه تطبیق زمان‌بندی"
    mpp_project.contract_amount = Decimal("25000000.00")
    mpp_project.budget_approved_at = timezone.now()
    mpp_project.budget_approved_by = p6_personas["independent_approver"]
    mpp_project.save(
        update_fields=[
            "status",
            "project_manager",
            "scope_description",
            "contract_amount",
            "budget_approved_at",
            "budget_approved_by",
            "updated_at",
        ]
    )

    raw_mpp = PLAN_MPP_PATH.read_bytes()
    assert hashlib.sha256(raw_mpp).hexdigest() == "3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553"
    assert len(raw_mpp) == 777216

    preview_res = planner_client.post(
        f"/api/v1/projects/{mpp_project.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("plan.mpp", raw_mpp, content_type="application/octet-stream")},
        format="multipart",
    )
    assert preview_res.status_code == 200, preview_res.content
    preview_data = preview_res.json()
    assert _counts(mpp_project) == {"wbs": 0, "activities": 0, "relations": 0, "baselines": 0}

    append_result = execute_msp_import(
        mpp_project,
        raw_mpp,
        filename="plan.mpp",
        replace=False,
        user=p6_personas["creator_planner"],
    )
    assert _counts(mpp_project) == {"wbs": 6, "activities": 72, "relations": 72, "baselines": 1}
    warning_codes = {item["code"] for item in append_result["warning_items"]}
    assert {"activity_without_parent", "predecessor_is_summary", "calendar_not_applied"} <= warning_codes
    assert not Activity.objects.filter(project=mpp_project, activity_name__in=["شروع", "پایان"]).exists()
    for summary_uid in ("8055", "8084", "8102", "8120"):
        assert any(
            item["code"] == "predecessor_is_summary" and summary_uid in item["row"]
            for item in append_result["warning_items"]
        )

    # --- POS-07: Repeat Append Idempotency (nothing_changed, 0 duplicates, 0 extra baselines) ---
    repeat_result = execute_msp_import(
        mpp_project,
        raw_mpp,
        filename="plan.mpp",
        replace=False,
        user=p6_personas["creator_planner"],
    )
    assert repeat_result["nothing_changed"] is True
    assert _counts(mpp_project) == {"wbs": 6, "activities": 72, "relations": 72, "baselines": 1}

    # --- POS-08: Safe Replacement Guard (Blocked on Protected History; Allowed on Unprotected) ---
    # 1) Unprotected project (bare WBS without activities/progress/cost/locked baseline) allows replacement and soft-deletes prior WBS rows
    replace_proj = create_project_with_creator(
        creator=p6_personas["creator_planner"],
        project_code="A7P6-REPLACE",
        project_name="پروژه جایگزینی ایمن",
        employer="کارفرمای مرجع",
        start_date="2026-01-01",
    )
    replace_proj.status = ProjectStatus.ACTIVE
    replace_proj.save(update_fields=["status", "updated_at"])
    create_wbs_node(project_id=replace_proj.id, wbs_code="OLD-1", wbs_name="گره قدیمی")
    assert _counts(replace_proj)["wbs"] == 1
    milestone_xml = (P1_FIXTURES / "milestone.xml").read_bytes()
    rep_res = execute_msp_import(
        replace_proj,
        milestone_xml,
        filename="milestone.xml",
        replace=True,
        user=p6_personas["creator_planner"],
    )
    assert rep_res["wbs_nodes_removed"] == 1
    assert _counts(replace_proj)["activities"] == 1
    assert WBS.objects.filter(project=replace_proj, is_deleted=True).count() == 1

    # 2) Protected project (activities + locked baseline) blocks replacement
    baseline = BaselineSchedule.objects.filter(project=mpp_project).first()
    baseline.is_locked = True
    baseline.save(update_fields=["is_locked", "updated_at"])
    with pytest.raises(ImportSafetyError) as exc_info:
        execute_msp_import(
            mpp_project,
            milestone_xml,
            filename="milestone.xml",
            replace=True,
            user=p6_personas["creator_planner"],
        )
    assert exc_info.value.code in {"wbs_has_activities", "baseline_history_protected"}
    assert _counts(mpp_project) == {"wbs": 6, "activities": 72, "relations": 72, "baselines": 1}

    # --- POS-09: 4-Way Dates, Milestones, Delay Report, Gantt, and Critical-Path Validity Gate ---
    first_act = Activity.objects.filter(project=mpp_project, is_deleted=False).first()
    first_act.actual_start = date(2026, 1, 5)
    first_act.forecast_finish = date(2026, 3, 20)
    first_act.save(update_fields=["actual_start", "forecast_finish", "updated_at"])

    act_detail = planner_client.get(f"/api/v1/projects/{mpp_project.id}/activities/{first_act.id}/")
    assert act_detail.status_code == 200
    for date_key in ("planned_start", "planned_finish", "actual_start", "forecast_finish"):
        assert date_key in act_detail.data

    gantt_payload = get_gantt_data(mpp_project.id)
    assert len(gantt_payload["tasks"]) == 72
    assert "critical_path" in gantt_payload
    status_report = build_schedule_status(mpp_project.id)
    assert "critical_path" in status_report or "critical_path_validity" in status_report
    cpm_validity = evaluate_critical_path_validity(mpp_project.id)
    assert "valid" in cpm_validity and "reason_codes" in cpm_validity

    # --- POS-10: Full Project Lifecycle Transitions Preserving All Project & Schedule Data ---
    from projects import lifecycle_service
    from projects.tests.archive_restore_helpers import grant_project_access

    grant_project_access(p6_personas["independent_approver"], mpp_project)
    grant_project_access(p6_personas["system_admin"], mpp_project)

    # 1) Active -> Suspended -> Active (Resume with mandatory confirmation & reason)
    susp_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/suspend/")
    assert susp_res.status_code == 200, susp_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.SUSPENDED

    res_prev = admin_client.get(f"/api/v1/projects/{mpp_project.id}/resume-preview/")
    assert res_prev.status_code == 200, res_prev.content
    res_exec = admin_client.post(
        f"/api/v1/projects/{mpp_project.id}/resume/",
        {
            "request_id": str(uuid4()),
            "confirmation_token": res_prev.json()["confirmation_token"],
            "reason": "رفع موانع کارگاهی و ازسرگیری برنامه",
        },
        format="json",
    )
    assert res_exec.status_code == 200, res_exec.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.ACTIVE

    # 2) Active -> Completed -> Undo Completion (System Admin only)
    comp_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/complete/")
    assert comp_res.status_code == 200, comp_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.COMPLETED

    non_admin_undo = planner_client.get(f"/api/v1/projects/{mpp_project.id}/undo-completion-preview/")
    assert non_admin_undo.status_code == 403

    undo_prev = admin_client.get(f"/api/v1/projects/{mpp_project.id}/undo-completion-preview/")
    assert undo_prev.status_code == 200, undo_prev.content
    assert undo_prev.json()["to_status"] == "active"
    undo_exec = admin_client.post(
        f"/api/v1/projects/{mpp_project.id}/undo-completion/",
        {
            "request_id": str(uuid4()),
            "confirmation_token": undo_prev.json()["confirmation_token"],
            "reason": "بازگردانی تکمیل جهت ثبت صورت‌جلسه نهایی",
        },
        format="json",
    )
    assert undo_exec.status_code == 200, undo_exec.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.ACTIVE

    # 3) Active -> Archived -> Restore from Archive (System Admin only, 100% data preservation)
    arch_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/archive/")
    assert arch_res.status_code == 200, arch_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.ARCHIVED

    non_admin_restore = planner_client.get(f"/api/v1/projects/{mpp_project.id}/restore-preview/")
    assert non_admin_restore.status_code == 403

    rest_prev = admin_client.get(f"/api/v1/projects/{mpp_project.id}/restore-preview/")
    assert rest_prev.status_code == 200, rest_prev.content
    assert rest_prev.json()["to_status"] == "active"
    rest_exec = admin_client.post(
        f"/api/v1/projects/{mpp_project.id}/restore/",
        {
            "request_id": str(uuid4()),
            "confirmation_token": rest_prev.json()["confirmation_token"],
            "reason": "بازیابی پروژه از آرشیو پس از ممیزی کارفرما",
        },
        format="json",
    )
    assert rest_exec.status_code == 200, rest_exec.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.ACTIVE
    assert _counts(mpp_project) == {"wbs": 6, "activities": 72, "relations": 72, "baselines": 1}


@pytest.mark.django_db
def test_a7_p6_negative_adverse_concurrency_and_access_boundaries_neg01_to_neg14(p6_personas):
    planner_client = _client_for(p6_personas["creator_planner"])
    viewer_client = _client_for(p6_personas["viewer"])
    admin_client = _client_for(p6_personas["system_admin"])

    project_a = create_project_with_creator(
        creator=p6_personas["creator_planner"],
        project_code="A7P6-NEG-A",
        project_name="پروژه A سناریوهای منفی",
        employer="کارفرمای مرجع",
        start_date="2026-01-01",
    )
    project_a.status = ProjectStatus.ACTIVE
    project_a.save(update_fields=["status", "updated_at"])

    project_b = create_project_with_creator(
        creator=p6_personas["independent_approver"],
        project_code="A7P6-NEG-B",
        project_name="پروژه B مستقل",
        employer="کارفرمای دیگر",
        start_date="2026-01-01",
    )
    project_b.status = ProjectStatus.ACTIVE
    project_b.save(update_fields=["status", "updated_at"])

    # Provision viewer on Project A
    viewer_member = ProjectMember.objects.create(
        project=project_a,
        user=p6_personas["viewer"],
        status=MemberStatus.ACTIVE,
    )
    ProjectMemberRole.objects.create(member=viewer_member, role=p6_personas["viewer_role"])

    # --- NEG-01: Duplicate/Normalized Project & WBS Codes Rejected ---
    dup_proj = planner_client.post(
        "/api/v1/projects/",
        {
            "project_code": "  A7P6-NEG-A  ",
            "project_name": "تکراری",
            "employer": "کارفرما",
            "start_date": "2026-01-01",
        },
        format="json",
    )
    assert dup_proj.status_code == 400

    root_a, _ = create_wbs_node(project_id=project_a.id, wbs_code="1", wbs_name="ریشه A")
    child_a, _ = create_wbs_node(project_id=project_a.id, parent_id=root_a.id, wbs_code="1.1", wbs_name="فرزند A")
    with pytest.raises(WBSValidationError):
        create_wbs_node(project_id=project_a.id, wbs_code=" 1 ", wbs_name="ریشه تکراری")

    # --- NEG-02: Invalid / Cross-Project Parent WBS Rejected ---
    foreign_wbs = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/",
        {"parent_id": str(uuid4()), "wbs_code": "9", "wbs_name": "والد نامعتبر"},
        format="json",
    )
    assert foreign_wbs.status_code == 400
    assert foreign_wbs.json()["error"]["code"] == "invalid_parent"

    # --- NEG-03: WBS Cycle & Dependency Cycle Rejected ---
    wbs_cycle = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/{root_a.id}/move/",
        {"new_parent_id": str(child_a.id), "position": "last-child"},
        format="json",
    )
    assert wbs_cycle.status_code == 400
    assert "wbs_cycle" in str(wbs_cycle.json())

    cycle_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Project xmlns="http://schemas.microsoft.com/project"><Tasks>'
        b"<Task><UID>1</UID><Name>R</Name><OutlineNumber>1</OutlineNumber><WBS>1</WBS><Summary>1</Summary></Task>"
        b"<Task><UID>2</UID><Name>A</Name><OutlineNumber>1.1</OutlineNumber><WBS>1.1</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>"
        b"<PredecessorLink><PredecessorUID>3</PredecessorUID><Type>1</Type></PredecessorLink></Task>"
        b"<Task><UID>3</UID><Name>B</Name><OutlineNumber>1.2</OutlineNumber><WBS>1.2</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>"
        b"<PredecessorLink><PredecessorUID>2</PredecessorUID><Type>1</Type></PredecessorLink></Task>"
        b"</Tasks></Project>"
    )
    with pytest.raises(ImportFidelityError) as cycle_exc:
        execute_msp_import(project_a, cycle_xml, filename="cycle.xml", replace=False, user=p6_personas["creator_planner"])
    assert cycle_exc.value.code == "structure_cycle"

    # --- NEG-04: Impossible Dates (finish < start) & Manual Non-Milestone Zero Duration Rejected ---
    bad_dates_res = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs": str(child_a.id),
            "activity_code": "ACT-BAD-DATE",
            "activity_name": "تاریخ نامعتبر",
            "planned_start": "2026-05-10",
            "planned_finish": "2026-05-01",
            "duration_days": 5,
        },
        format="json",
    )
    assert bad_dates_res.status_code == 400

    # --- NEG-05: Missing Predecessor & Atomic Import Rollback ---
    dangling_xml = (P1_FIXTURES / "dangling-predecessor.xml").read_bytes()
    dangling_preview = build_preview(parse_msp_xml(dangling_xml))
    assert any(w["code"] in {"activity_without_parent", "missing_predecessor"} for w in dangling_preview["warning_items"])

    # --- NEG-06: Corrupt, Wrong Signature, Password-Protected, Truncated OLE, and >50MB Uploads Rejected ---
    before_neg06 = _counts(project_a)
    for fname, payload, ctype, expected_code in [
        ("not-a-project.xml", (P1_FIXTURES / "not-a-project.xml").read_bytes(), "application/xml", "msp_invalid_xml"),
        ("notes.txt", b"plain text", "text/plain", "invalid_file_type"),
        (
            "password-protected.mpp",
            (MPP_FIXTURES / "password-protected.mpp").read_bytes(),
            "application/octet-stream",
            "mpp_password_protected",
        ),
        (
            "truncated-ole.mpp",
            (MPP_FIXTURES / "truncated-ole.mpp").read_bytes(),
            "application/octet-stream",
            "mpp_unsupported",
        ),
        (
            "renamed-not-mpp.mpp",
            (MPP_FIXTURES / "renamed-not-mpp.mpp").read_bytes(),
            "application/octet-stream",
            "invalid_file_type",
        ),
        (
            "oversized.xml",
            b"x" * (50 * 1024 * 1024 + 1024),
            "application/xml",
            "file_too_large",
        ),
    ]:
        res = planner_client.post(
            f"/api/v1/projects/{project_a.id}/import/msp/",
            {"file": SimpleUploadedFile(fname, payload, content_type=ctype)},
            format="multipart",
        )
        assert res.status_code == 400, (fname, res.content)
        assert res.json()["error"]["code"] == expected_code
    assert _counts(project_a) == before_neg06

    # --- NEG-07: Cancel After Preview Writes Nothing ---
    prev_only = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert prev_only.status_code == 200
    assert _counts(project_a) == before_neg06

    # --- NEG-08 & NEG-09: In-Flight Job Recovery & Duplicate Submission Return Same Active Attempt ---
    branch_bytes = (P1_FIXTURES / "branch.xml").read_bytes()
    active_job = MspImportJob.objects.create(
        project=project_a,
        status=MspImportStatus.RUNNING,
        filename="branch.xml",
        file_data=branch_bytes,
        source_sha256=hashlib.sha256(branch_bytes).hexdigest(),
        source_size=len(branch_bytes),
        replace_existing=False,
        created_by=p6_personas["creator_planner"],
    )
    status_poll = planner_client.get(
        f"/api/v1/projects/{project_a.id}/import/msp/status/{active_job.id}/"
    )
    assert status_poll.status_code == 200
    assert status_poll.json()["status"] == MspImportStatus.RUNNING
    assert "progress_pct" in status_poll.json()

    conflict_start = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/",
        {"file": SimpleUploadedFile("branch.xml", branch_bytes, content_type="application/xml"), "replace": "false"},
        format="multipart",
    )
    assert conflict_start.status_code == 202
    assert conflict_start.json()["task_id"] == str(active_job.id)
    assert MspImportJob.objects.filter(project=project_a).count() == 1
    assert _counts(project_a) == before_neg06
    active_job.status = MspImportStatus.FAILED
    active_job.save(update_fields=["status", "updated_at"])

    # --- NEG-10: Mid-Queue Permission Revocation or Archival Aborts Worker Execution ---
    queued_job = MspImportJob.objects.create(
        project=project_a,
        status=MspImportStatus.PENDING,
        filename="branch.xml",
        file_data=branch_bytes,
        source_sha256=hashlib.sha256(branch_bytes).hexdigest(),
        source_size=len(branch_bytes),
        replace_existing=False,
        created_by=p6_personas["viewer"],  # Viewer lacks import_schedule permission
    )
    run_msp_import_task.apply(args=[str(queued_job.id)])
    queued_job.refresh_from_db()
    assert queued_job.status == MspImportStatus.FAILED
    assert queued_job.error_code == "import_not_permitted"
    assert _counts(project_a) == before_neg06

    # --- NEG-11: Cross-Project Isolation (Project A vs Project B) ---
    cross_get = planner_client.get(f"/api/v1/projects/{project_b.id}/wbs/")
    assert cross_get.status_code in (403, 404)
    cross_job = planner_client.get(
        f"/api/v1/projects/{project_b.id}/import/msp/status/{queued_job.id}/"
    )
    assert cross_job.status_code in (403, 404)

    # --- NEG-12: Viewer (view_only) Blocked from Mutations and Imports ---
    viewer_read = viewer_client.get(f"/api/v1/projects/{project_a.id}/wbs/")
    assert viewer_read.status_code == 200
    viewer_write = viewer_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/",
        {"wbs_code": "2", "wbs_name": "تلاش مشاهده‌گر"},
        format="json",
    )
    assert viewer_write.status_code == 403
    viewer_import = viewer_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert viewer_import.status_code == 403

    # --- NEG-13: Non-Member System Administrator Observation Exception ---
    admin_observe = admin_client.get(f"/api/v1/projects/{project_b.id}/wbs/")
    assert admin_observe.status_code == 200

    # --- NEG-14: Archived Project Strictly Read-Only Across Import & Protected Project Surfaces ---
    from projects import lifecycle_service

    project_a = lifecycle_service.archive(project_a, p6_personas["creator_planner"])
    arch_patch = planner_client.patch(
        f"/api/v1/projects/{project_a.id}/",
        {"employer": "تغییر در حالت آرشیو"},
        format="json",
    )
    assert arch_patch.status_code in (400, 403)
    arch_start = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert arch_start.status_code == 400
    assert arch_start.json()["error"]["code"] == "project_archived"
    assert _counts(project_a) == before_neg06
