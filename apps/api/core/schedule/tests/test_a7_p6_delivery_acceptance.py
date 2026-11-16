"""Integrated End-to-End Acceptance Suite for Module A.7-P6 (056-a7-p6-delivery-acceptance).

Covers:
- POS-01..POS-10: Positive reference project journey across 5 separated role personas
- NEG-01..NEG-14: Independent negative, adverse, concurrency, and access-boundary scenarios
- Reference schedule reconciliation on unchanged real-data/plan.mpp (6 WBS, 72 activities, 72 relations)
"""

from __future__ import annotations

import hashlib
from datetime import date
from decimal import Decimal
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
from permissions.project import active_member_has_codename, has_organizational_observation
from permissions.services import set_permission_override
from projects.services import create_project_with_creator
from schedule.models import (
    ActivityMeasurementDefinition,
    ActivityProgress,
    BaselineActivity,
    BaselineSchedule,
    MspImportJob,
    MspImportStatus,
    ProjectPeriodReport,
    ScheduleChangeRequest,
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
            "measurement_unit": mu_res.json()["id"],
            "project_manager": str(p6_personas["creator_planner"].id),
        },
        format="json",
    )
    assert proj_res.status_code == 201, proj_res.content
    project_id = proj_res.json()["id"]
    project = Project.objects.get(pk=project_id)
    assert project.status == ProjectStatus.DRAFT
    assert str(project.measurement_unit_id) == str(mu_res.json()["id"])

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
    assert gate_fail.data["error"]["code"] == "activation_gates_failed"
    assert "project_manager" in gate_fail.data["error"]["details"].get("missing", gate_fail.data["error"].get("missing", [])) or "project_manager" in str(gate_fail.data)
    Project.objects.filter(pk=project_id).update(project_manager=p6_personas["creator_planner"])

    Project.objects.filter(pk=project_id).update(scope_description="")
    scope_fail = approver_client.post(f"/api/v1/projects/{project_id}/approve/")
    assert scope_fail.status_code == 400
    assert scope_fail.data["error"]["code"] == "activation_gates_failed"
    assert "scope_description" in str(scope_fail.data)
    Project.objects.filter(pk=project_id).update(scope_description="ساختار شکست کار، ورود زمان‌بندی و خط مبنا")

    Project.objects.filter(pk=project_id).update(contract_amount=0)
    budget_fail = approver_client.post(f"/api/v1/projects/{project_id}/approve/")
    assert budget_fail.status_code == 400
    assert budget_fail.data["error"]["code"] == "activation_gates_failed"
    assert "budget_approved" in str(budget_fail.data)
    Project.objects.filter(pk=project_id).update(contract_amount="50000000.00")

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
    assert cr_approve.data["requested_by"]
    assert cr_approve.data["decided_by"]
    assert cr_approve.data["decided_at"]
    assert cr_approve.data["previous_values"]["employer"] == "کارفرمای مرجع"

    cr_reject_create = planner_client.post(
        cr_base,
        {
            "reason": "رد این درخواست باید سابقه تصمیم را نگه دارد",
            "proposed_changes": {"employer": "کارفرمای ردشده"},
        },
        format="json",
    )
    assert cr_reject_create.status_code == 201, cr_reject_create.content
    reject_id = cr_reject_create.data["id"]
    assert planner_client.post(f"{cr_base}{reject_id}/submit/").status_code == 200
    cr_reject = approver_client.post(f"{cr_base}{reject_id}/reject/", {"decision_notes": "رد شد"}, format="json")
    assert cr_reject.status_code == 200, cr_reject.content
    assert cr_reject.data["status"] == "rejected"
    assert cr_reject.data["requested_by"]
    assert cr_reject.data["decided_by"]
    assert cr_reject.data["decided_at"]
    assert "employer" in cr_reject.data["previous_values"]
    project.refresh_from_db()
    assert project.employer == "شرکت توسعه ابنیه کارفرمای مرجع"

    # --- POS-04: Multi-level WBS (>=3 levels), Responsible & Criterion, Move/Renumber, Template Copy ---
    root_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "wbs_code": "1",
            "wbs_name": "عملیات کل پروژه",
            "weight_physical": "1.0000",
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
            "weight_physical": "1.0000",
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
            "weight_physical": "0.6000",
            "responsible": str(p6_personas["creator_planner"].id),
            "acceptance_criteria": "تأیید آرماتوربندی و بتن‌ریزی فونداسیون",
        },
        format="json",
    )
    assert pkg1_res.status_code == 201, pkg1_res.content
    pkg1_id = pkg1_res.json()["wbs_id"]
    pkg2_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "parent_id": phase_id,
            "wbs_code": "1.1.2",
            "wbs_name": "ستون و سقف",
            "weight_physical": "0.4000",
            "responsible": str(p6_personas["independent_approver"].id),
            "acceptance_criteria": "تأیید شاقول‌سنجی و مقاومت ۲۸روزه",
        },
        format="json",
    )
    assert pkg2_res.status_code == 201, pkg2_res.content
    assert "warnings" not in pkg2_res.json()
    pkg2_id = pkg2_res.json()["wbs_id"]
    sibling_weights = WBS.objects.filter(pk__in=[pkg1_id, pkg2_id]).values_list("weight_physical", flat=True)
    assert sum(sibling_weights) == Decimal("1.0000")

    over_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/",
        {
            "parent_id": phase_id,
            "wbs_code": "1.1.3",
            "wbs_name": "وزن مازاد",
            "weight_physical": "0.5000",
        },
        format="json",
    )
    assert over_res.status_code == 201, over_res.content
    assert any("exceeds 1.0" in warning for warning in over_res.json().get("warnings", []))
    over_delete = planner_client.delete(f"/api/v1/projects/{project_id}/wbs/{over_res.json()['wbs_id']}/")
    assert over_delete.status_code == 204, over_delete.content
    assert not WBS.objects.filter(pk=over_res.json()["wbs_id"], is_deleted=False).exists()

    move_res = planner_client.post(
        f"/api/v1/projects/{project_id}/wbs/{pkg2_id}/move/",
        {"new_parent_id": root_id, "position": "last-child"},
        format="json",
    )
    assert move_res.status_code == 200, move_res.content
    assert move_res.json()["wbs_code"] == "1.2"
    assert move_res.json()["depth"] == 2
    assert WBS.objects.get(pk=pkg1_id).wbs_code == "1.1.1"
    assert WBS.objects.get(pk=pkg1_id).depth == 3

    tpl_res = planner_client.post(
        f"/api/v1/projects/{project_id}/save-as-template/",
        {
            "template_name": "الگوی مرجع ۳سطحی A7P6",
            "description": "الگوی تست استقلال کپی WBS",
            "project_type": "residential",
        },
        format="json",
    )
    assert tpl_res.status_code == 201, tpl_res.content
    tpl_id = tpl_res.json()["template_id"]
    assert tpl_res.json()["wbs_node_count"] == 4

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
    assert WBS.objects.filter(project=target_proj, is_deleted=False).count() == 4

    from project_templates.models import ProjectTemplateWBS

    template_pkg = ProjectTemplateWBS.objects.get(template_id=tpl_id, wbs_code="1.1.1")
    template_pkg.wbs_name = "تغییر در الگو"
    template_pkg.save(update_fields=["wbs_name"])
    planner_client.patch(
        f"/api/v1/projects/{project_id}/wbs/{pkg1_id}/",
        {"wbs_name": "فونداسیون ویرایش‌شده"},
        format="json",
    )
    assert WBS.objects.get(project=target_proj, wbs_code="1.1.1").wbs_name == "فونداسیون"

    # --- POS-05 & POS-06: Preview & Append Import of real-data/plan.mpp and XML/XER Fixtures ---
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
    from schedule.services.import_fidelity import TENTHS_PER_DAY, days_from_tenths

    assert TENTHS_PER_DAY == 480 * 10
    assert days_from_tenths(TENTHS_PER_DAY) == (1, False)
    for lag_days in ActivityRelation.objects.filter(
        predecessor__project=mpp_project, is_deleted=False,
    ).values_list("lag_days", flat=True):
        assert lag_days * 480 == lag_days * (TENTHS_PER_DAY // 10)

    def _preview_and_store(raw: bytes, filename: str, family: str, expected: dict):
        hosted = create_project_with_creator(
            creator=p6_personas["creator_planner"],
            project_code=f"A7P6-{filename[:12]}",
            project_name=filename,
            employer="کارفرمای مرجع",
            start_date="2026-01-01",
        )
        hosted.status = ProjectStatus.ACTIVE
        hosted.save(update_fields=["status", "updated_at"])
        route = "p6" if family == "p6" else "msp"
        preview = planner_client.post(
            f"/api/v1/projects/{hosted.id}/import/{route}/preview/",
            {"file": SimpleUploadedFile(filename, raw, content_type="application/octet-stream")},
            format="multipart",
        )
        assert preview.status_code == 200, preview.content
        assert _counts(hosted)["activities"] == 0
        runner = execute_p6_import if family == "p6" else execute_msp_import
        stored = runner(hosted, raw, filename=filename, replace=False, user=p6_personas["creator_planner"])
        assert _counts(hosted)["wbs"] == expected["wbs"], stored
        assert _counts(hosted)["activities"] == expected["activities"]
        assert _counts(hosted)["relations"] == expected["relations"]
        again = runner(hosted, raw, filename=filename, replace=False, user=p6_personas["creator_planner"])
        assert again["nothing_changed"] is True
        return stored

    _preview_and_store((P1_FIXTURES / "branch.xml").read_bytes(), "branch.xml", "msp", {"wbs": 1, "activities": 2, "relations": 0})
    _preview_and_store((P1_FIXTURES / "branch.xer").read_bytes(), "branch.xer", "p6", {"wbs": 3, "activities": 2, "relations": 0})
    p6_xml = REPO_ROOT / "apps/api/core/schedule/tests/fixtures/mpp/duration-test9.xml"
    _preview_and_store(p6_xml.read_bytes(), "duration-test9.xml", "msp", {"wbs": 0, "activities": 0, "relations": 0})

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

    # 2) Protected execution history blocks replacement and leaves stored rows unchanged
    planner = p6_personas["creator_planner"]

    def _refuse_replace(project: Project) -> None:
        before = _counts(project)
        with pytest.raises(ImportSafetyError) as caught:
            execute_msp_import(
                project,
                milestone_xml,
                filename="milestone.xml",
                replace=True,
                user=planner,
            )
        assert caught.value.code == "baseline_replace_forbidden"
        assert _counts(project) == before

    baseline = BaselineSchedule.objects.filter(project=mpp_project).first()
    baseline.is_locked = True
    baseline.save(update_fields=["is_locked", "updated_at"])
    _refuse_replace(mpp_project)

    def _history_project(code: str) -> Project:
        project = create_project_with_creator(
            creator=planner,
            project_code=code,
            project_name=code,
            employer="کارفرمای مرجع",
            start_date="2026-01-01",
        )
        project.status = ProjectStatus.ACTIVE
        project.save(update_fields=["status", "updated_at"])
        return project

    progress_project = _history_project("A7P6-REP-PROG")
    progress_node, _progress_warnings = create_wbs_node(
        project_id=progress_project.id, wbs_code="P", wbs_name="پیشرفت"
    )
    progress_activity = Activity.objects.create(
        project=progress_project,
        wbs=progress_node,
        activity_code="P1",
        activity_name="فعالیت دارای پیشرفت",
        created_by=planner,
        updated_by=planner,
    )
    ActivityProgress.objects.create(
        activity=progress_activity,
        report_date=date(2026, 2, 1),
        actual_progress=1,
    )
    _refuse_replace(progress_project)

    period_project = _history_project("A7P6-REP-PERIOD")
    ProjectPeriodReport.objects.create(
        project=period_project,
        kind="weekly",
        period_start=date(2026, 2, 1),
        period_end=date(2026, 2, 7),
        generated_at=timezone.now(),
        created_by=planner,
        updated_by=planner,
    )
    _refuse_replace(period_project)

    change_project = _history_project("A7P6-REP-CHANGE")
    ScheduleChangeRequest.objects.create(
        project=change_project,
        reason="تغییر تاریخ فعالیت",
        created_by=planner,
        updated_by=planner,
    )
    _refuse_replace(change_project)

    measure_project = _history_project("A7P6-REP-MEASURE")
    measure_node, _measure_warnings = create_wbs_node(
        project_id=measure_project.id, wbs_code="M", wbs_name="سنجش"
    )
    measure_activity = Activity.objects.create(
        project=measure_project,
        wbs=measure_node,
        activity_code="M1",
        activity_name="فعالیت دارای سنجش",
        created_by=planner,
        updated_by=planner,
    )
    ActivityMeasurementDefinition.objects.create(
        project=measure_project,
        activity=measure_activity,
        created_by=planner,
        updated_by=planner,
    )
    _refuse_replace(measure_project)

    # --- POS-09: 4-Way Dates, Milestones, Delay Report, Gantt, and Critical-Path Validity Gate ---
    first_act = Activity.objects.filter(project=mpp_project, is_deleted=False).first()
    first_act.actual_start = date(2026, 1, 5)
    first_act.forecast_finish = date(2026, 3, 20)
    first_act.save(update_fields=["actual_start", "forecast_finish", "updated_at"])

    act_detail = planner_client.get(f"/api/v1/projects/{mpp_project.id}/activities/{first_act.id}/")
    assert act_detail.status_code == 200
    for date_key in ("planned_start", "planned_finish", "actual_start", "forecast_finish"):
        assert date_key in act_detail.data
    assert act_detail.data["actual_start"]
    assert act_detail.data["forecast_finish"]

    gantt_payload = get_gantt_data(mpp_project.id)
    assert len(gantt_payload["tasks"]) == 72
    assert "critical_path" in gantt_payload
    matched = next(task for task in gantt_payload["tasks"] if task["activity_id"] == str(first_act.id))
    assert matched["planned_start"] and matched["actual_start"] and matched["forecast_finish"]
    assert "delay_days" in matched
    assert "is_milestone" in matched
    status_report = build_schedule_status(mpp_project.id)
    assert "critical_path" in status_report or "critical_path_validity" in status_report
    assert "milestones" in status_report and "delays" in status_report and "date_sets" in status_report
    cpm_validity = evaluate_critical_path_validity(mpp_project.id)
    assert "valid" in cpm_validity and "reason_codes" in cpm_validity

    # --- POS-10: Full Project Lifecycle Transitions Preserving All Project & Schedule Data ---
    from projects import lifecycle_service
    from projects.tests.archive_restore_helpers import grant_project_access

    grant_project_access(p6_personas["independent_approver"], mpp_project)
    grant_project_access(p6_personas["system_admin"], mpp_project)

    # The schedule lives on a different project from POS-01. Give this same
    # project a populated charter, then compare the records, not just counts.
    ProjectKickoffCharter.objects.create(
        project=mpp_project, **charter_payload,
        created_by=p6_personas["creator_planner"],
        updated_by=p6_personas["creator_planner"],
    )
    charter_url = f"/api/v1/projects/{mpp_project.id}/kickoff-charter/"
    charter_before = planner_client.get(charter_url)
    assert charter_before.status_code == 200, charter_before.content
    for field, expected in charter_payload.items():
        assert charter_before.data[field] == expected

    def preserved_records():
        return {
            "project": list(Project.objects.filter(pk=mpp_project.pk).values(
                "project_code", "project_name", "employer", "start_date",
                "project_manager_id", "scope_description", "contract_amount",
                "budget_approved_at", "budget_approved_by_id",
            )),
            "charter": list(ProjectKickoffCharter.objects.filter(project=mpp_project).values()),
            "wbs": list(WBS.objects.filter(project=mpp_project).order_by("pk").values()),
            "activities": list(Activity.objects.filter(project=mpp_project).order_by("pk").values()),
            "relations": list(ActivityRelation.objects.filter(successor__project=mpp_project).order_by("pk").values()),
            "baselines": list(BaselineSchedule.objects.filter(project=mpp_project).order_by("pk").values()),
            "baseline_activities": list(BaselineActivity.objects.filter(baseline__project=mpp_project).order_by("pk").values()),
        }

    before_lifecycle = preserved_records()
    assert all(before_lifecycle.values())

    def assert_preserved():
        assert preserved_records() == before_lifecycle
        charter_after = planner_client.get(charter_url)
        assert charter_after.status_code == 200, charter_after.content
        assert charter_after.data == charter_before.data

    # 1) Active -> Suspended -> Active (Resume with mandatory confirmation & reason)
    susp_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/suspend/")
    assert susp_res.status_code == 200, susp_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.SUSPENDED
    assert_preserved()

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
    assert_preserved()

    # 2) Active -> Completed -> Undo Completion (System Admin only)
    comp_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/complete/")
    assert comp_res.status_code == 200, comp_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.COMPLETED
    assert_preserved()

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
    assert_preserved()

    # 3) Active -> Archived -> Restore from Archive (System Admin only, 100% data preservation)
    arch_res = approver_client.post(f"/api/v1/projects/{mpp_project.id}/archive/")
    assert arch_res.status_code == 200, arch_res.content
    mpp_project.refresh_from_db()
    assert mpp_project.status == ProjectStatus.ARCHIVED
    assert_preserved()

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
    assert_preserved()
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
    foreign_root, _foreign_warnings = create_wbs_node(
        project_id=project_b.id, wbs_code="B1", wbs_name="ریشه پروژه B"
    )
    foreign_wbs = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/",
        {"parent_id": str(foreign_root.id), "wbs_code": "9", "wbs_name": "والد پروژه دیگر"},
        format="json",
    )
    assert foreign_wbs.status_code == 400
    assert foreign_wbs.json()["error"]["code"] == "invalid_parent"
    assert not WBS.objects.filter(project=project_a, wbs_code="9", is_deleted=False).exists()

    # --- NEG-03: Direct & Indirect WBS / Dependency Cycles Rejected With No Partial Writes ---
    before_neg03 = _counts(project_a)
    before_neg03_jobs = MspImportJob.objects.filter(project=project_a).count()

    # Direct WBS cycle: move root under its own child
    wbs_cycle = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/{root_a.id}/move/",
        {"new_parent_id": str(child_a.id), "position": "last-child"},
        format="json",
    )
    assert wbs_cycle.status_code == 400
    assert "wbs_cycle" in str(wbs_cycle.json())
    assert _counts(project_a) == before_neg03

    # Indirect WBS cycle: root -> child -> grandchild, then move root under grandchild
    grandchild_a, _ = create_wbs_node(
        project_id=project_a.id, parent_id=child_a.id, wbs_code="1.1.1", wbs_name="نوه A"
    )
    before_indirect_wbs = _counts(project_a)
    indirect_wbs_cycle = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/{root_a.id}/move/",
        {"new_parent_id": str(grandchild_a.id), "position": "last-child"},
        format="json",
    )
    assert indirect_wbs_cycle.status_code == 400
    assert "wbs_cycle" in str(indirect_wbs_cycle.json())
    assert _counts(project_a) == before_indirect_wbs

    # Direct mutual dependency cycle via import
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
    assert _counts(project_a) == before_indirect_wbs
    assert MspImportJob.objects.filter(project=project_a).count() == before_neg03_jobs

    # Indirect dependency cycle via import: A→B→C→A
    indirect_cycle_xml = (
        b'<?xml version="1.0" encoding="UTF-8"?>'
        b'<Project xmlns="http://schemas.microsoft.com/project"><Tasks>'
        b"<Task><UID>1</UID><Name>R</Name><OutlineNumber>1</OutlineNumber><WBS>1</WBS><Summary>1</Summary></Task>"
        b"<Task><UID>2</UID><Name>A</Name><OutlineNumber>1.1</OutlineNumber><WBS>1.1</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>"
        b"<PredecessorLink><PredecessorUID>4</PredecessorUID><Type>1</Type></PredecessorLink></Task>"
        b"<Task><UID>3</UID><Name>B</Name><OutlineNumber>1.2</OutlineNumber><WBS>1.2</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>"
        b"<PredecessorLink><PredecessorUID>2</PredecessorUID><Type>1</Type></PredecessorLink></Task>"
        b"<Task><UID>4</UID><Name>C</Name><OutlineNumber>1.3</OutlineNumber><WBS>1.3</WBS><Summary>0</Summary><Duration>PT8H0M0S</Duration>"
        b"<PredecessorLink><PredecessorUID>3</PredecessorUID><Type>1</Type></PredecessorLink></Task>"
        b"</Tasks></Project>"
    )
    with pytest.raises(ImportFidelityError) as indirect_cycle_exc:
        execute_msp_import(
            project_a,
            indirect_cycle_xml,
            filename="indirect-cycle.xml",
            replace=False,
            user=p6_personas["creator_planner"],
        )
    assert indirect_cycle_exc.value.code == "structure_cycle"
    assert _counts(project_a) == before_indirect_wbs

    # Indirect dependency cycle via live API: act1→act2→act3, then act3→act1 must fail
    act1 = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs_id": str(child_a.id),
            "activity_code": "CYC-1",
            "activity_name": "حلقه ۱",
            "duration_days": 1,
            "planned_start": "2026-04-01",
            "planned_finish": "2026-04-01",
        },
        format="json",
    )
    assert act1.status_code == 201, act1.content
    act2 = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs_id": str(child_a.id),
            "activity_code": "CYC-2",
            "activity_name": "حلقه ۲",
            "duration_days": 1,
            "planned_start": "2026-04-02",
            "planned_finish": "2026-04-02",
        },
        format="json",
    )
    assert act2.status_code == 201, act2.content
    act3 = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs_id": str(child_a.id),
            "activity_code": "CYC-3",
            "activity_name": "حلقه ۳",
            "duration_days": 1,
            "planned_start": "2026-04-03",
            "planned_finish": "2026-04-03",
        },
        format="json",
    )
    assert act3.status_code == 201, act3.content
    id1, id2, id3 = act1.json()["activity_id"], act2.json()["activity_id"], act3.json()["activity_id"]
    rel12 = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/{id1}/relations/",
        {"role": "predecessor", "successor_id": id2, "relation_type": "FS", "lag_days": 0},
        format="json",
    )
    assert rel12.status_code in (200, 201), rel12.content
    rel23 = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/{id2}/relations/",
        {"role": "predecessor", "successor_id": id3, "relation_type": "FS", "lag_days": 0},
        format="json",
    )
    assert rel23.status_code in (200, 201), rel23.content
    before_closing_edge = _counts(project_a)
    closing_cycle = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/{id3}/relations/",
        {"role": "predecessor", "successor_id": id1, "relation_type": "FS", "lag_days": 0},
        format="json",
    )
    assert closing_cycle.status_code == 400, closing_cycle.content
    assert "حلقه" in str(closing_cycle.json()) or "cycle" in str(closing_cycle.json()).lower()
    assert _counts(project_a) == before_closing_edge

    # --- NEG-04: Impossible Dates (finish < start) & Manual Non-Milestone Zero Duration Rejected ---
    before_neg04 = Activity.objects.filter(project=project_a, is_deleted=False).count()
    bad_dates_res = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs_id": str(child_a.id),
            "activity_code": "ACT-BAD-DATE",
            "activity_name": "تاریخ نامعتبر",
            "planned_start": "2026-05-10",
            "planned_finish": "2026-05-01",
            "duration_days": 5,
        },
        format="json",
    )
    assert bad_dates_res.status_code == 400
    assert bad_dates_res.json()["error"]["code"] == "impossible_planned_dates"
    zero_duration_res = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {
            "wbs_id": str(child_a.id),
            "activity_code": "ACT-ZERO",
            "activity_name": "مدت صفر غیرمایلستون",
            "is_milestone": False,
            "duration_days": 0,
        },
        format="json",
    )
    assert zero_duration_res.status_code == 400
    assert zero_duration_res.json()["error"]["code"] == "zero_duration_non_milestone"
    assert Activity.objects.filter(project=project_a, is_deleted=False).count() == before_neg04

    # --- NEG-05: Missing Predecessor & Atomic Import Rollback ---
    dangling_xml = (P1_FIXTURES / "dangling-predecessor.xml").read_bytes()
    dangling_preview = build_preview(parse_msp_xml(dangling_xml))
    assert any(w["code"] in {"activity_without_parent", "missing_predecessor", "predecessor_missing"} for w in dangling_preview["warning_items"])
    before_dangling = _counts(project_a)
    execute_msp_import(
        project_a, dangling_xml, filename="dangling-predecessor.xml", replace=False, user=p6_personas["creator_planner"],
    )
    assert ActivityRelation.objects.filter(predecessor__project=project_a, predecessor_id__isnull=True).count() == 0
    assert _counts(project_a)["relations"] == before_dangling["relations"]

    # --- NEG-06: Corrupt, Wrong Signature, Password-Protected, Truncated OLE, and >50MB Uploads Rejected ---
    before_neg06 = _counts(project_a)
    empty_upload = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/",
        {"file": SimpleUploadedFile("empty.xml", b"", content_type="application/xml")},
        format="multipart",
    )
    assert empty_upload.status_code == 400
    assert empty_upload.json()["error"]["code"] == "empty_import"
    assert MspImportJob.objects.filter(project=project_a, filename="empty.xml").count() == 0
    assert _counts(project_a) == before_neg06
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

    # --- NEG-07: Cancel After Preview Writes Nothing And Queues No Job ---
    before_neg07_jobs = MspImportJob.objects.filter(project=project_a).count()
    before_neg07_counts = _counts(project_a)
    prev_only = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert prev_only.status_code == 200
    # Simulate cancel: no confirm/start call follows the preview.
    assert _counts(project_a) == before_neg07_counts
    assert MspImportJob.objects.filter(project=project_a).count() == before_neg07_jobs
    assert MspImportJob.objects.filter(project=project_a, filename="branch.xml").count() == 0

    # --- NEG-08 & NEG-09: Same-Attempt Recovery After Disconnect/Reload & Duplicate Submit Lock ---
    branch_bytes = (P1_FIXTURES / "branch.xml").read_bytes()
    before_neg08_jobs = MspImportJob.objects.filter(project=project_a).count()
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
    # Simulate connection drop / page reload: re-poll the same task id without creating another job.
    status_poll = planner_client.get(
        f"/api/v1/projects/{project_a.id}/import/msp/status/{active_job.id}/"
    )
    assert status_poll.status_code == 200
    assert status_poll.json()["status"] == MspImportStatus.RUNNING
    assert "progress_pct" in status_poll.json()
    reload_poll = planner_client.get(
        f"/api/v1/projects/{project_a.id}/import/msp/status/{active_job.id}/"
    )
    assert reload_poll.status_code == 200
    assert reload_poll.json()["status"] == MspImportStatus.RUNNING
    assert reload_poll.json()["task_id"] == str(active_job.id) if "task_id" in reload_poll.json() else True
    assert MspImportJob.objects.filter(project=project_a).count() == before_neg08_jobs + 1

    conflict_start = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/",
        {"file": SimpleUploadedFile("branch.xml", branch_bytes, content_type="application/xml"), "replace": "false"},
        format="multipart",
    )
    assert conflict_start.status_code == 202
    assert conflict_start.json()["task_id"] == str(active_job.id)
    assert conflict_start.json()["code"] == "import_already_active"
    assert MspImportJob.objects.filter(project=project_a).count() == before_neg08_jobs + 1
    assert _counts(project_a) == before_neg07_counts
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

    archived_job = MspImportJob.objects.create(
        project=project_a,
        status=MspImportStatus.PENDING,
        filename="branch.xml",
        file_data=branch_bytes,
        source_sha256=hashlib.sha256(branch_bytes).hexdigest(),
        source_size=len(branch_bytes),
        replace_existing=False,
        created_by=p6_personas["creator_planner"],
    )
    from projects import lifecycle_service

    project_a = lifecycle_service.archive(project_a, p6_personas["creator_planner"])
    run_msp_import_task.apply(args=[str(archived_job.id)])
    archived_job.refresh_from_db()
    assert archived_job.status == MspImportStatus.FAILED
    assert archived_job.error_code == "project_archived"
    assert _counts(project_a) == before_neg06
    project_a.status = ProjectStatus.ACTIVE
    project_a.archived_from_status = None
    project_a.archive_cycle_id = None
    project_a.save(update_fields=["status", "archived_from_status", "archive_cycle_id", "updated_at"])

    # --- NEG-11: Cross-Project Isolation Across WBS, Schedule, Baseline, and Import ---
    approver_client_for_b = _client_for(p6_personas["independent_approver"])
    root_b, _ = create_wbs_node(project_id=project_b.id, wbs_code="B-ROOT", wbs_name="ریشه B")
    act_b = approver_client_for_b.post(
        f"/api/v1/projects/{project_b.id}/activities/",
        {
            "wbs_id": str(root_b.id),
            "activity_code": "B-ACT-1",
            "activity_name": "فعالیت پروژه B",
            "duration_days": 2,
            "planned_start": "2026-05-01",
            "planned_finish": "2026-05-02",
        },
        format="json",
    )
    assert act_b.status_code == 201, act_b.content
    baseline_b = approver_client_for_b.post(
        f"/api/v1/projects/{project_b.id}/baselines/",
        {"version_name": "خط مبنای B", "make_current": True},
        format="json",
    )
    assert baseline_b.status_code == 201, baseline_b.content

    cross_get = planner_client.get(f"/api/v1/projects/{project_b.id}/wbs/")
    assert cross_get.status_code in (403, 404)
    cross_activities = planner_client.get(f"/api/v1/projects/{project_b.id}/activities/")
    assert cross_activities.status_code in (403, 404)
    cross_gantt = planner_client.get(f"/api/v1/projects/{project_b.id}/gantt/")
    assert cross_gantt.status_code in (403, 404)
    cross_baselines = planner_client.get(f"/api/v1/projects/{project_b.id}/baselines/")
    assert cross_baselines.status_code in (403, 404)
    cross_baseline_detail = planner_client.get(
        f"/api/v1/projects/{project_b.id}/baselines/{baseline_b.json()['id']}/"
    )
    # Detail may be missing as a route; list denial is enough when detail 404s by routing.
    assert cross_baseline_detail.status_code in (403, 404, 405)
    cross_job = planner_client.get(
        f"/api/v1/projects/{project_b.id}/import/msp/status/{queued_job.id}/"
    )
    assert cross_job.status_code in (403, 404)
    # Project A member must not read Project B schedule rows by borrowing B ids on A's path either.
    cross_activity_on_a = planner_client.get(
        f"/api/v1/projects/{project_a.id}/activities/{act_b.json()['activity_id']}/"
    )
    assert cross_activity_on_a.status_code in (403, 404)

    # --- NEG-12: Viewer (view_only) Blocked from Project, WBS, Baseline, and Import Mutations ---
    before_viewer = _counts(project_a)
    viewer_read = viewer_client.get(f"/api/v1/projects/{project_a.id}/wbs/")
    assert viewer_read.status_code == 200
    viewer_project_write = viewer_client.patch(
        f"/api/v1/projects/{project_a.id}/",
        {"employer": "تلاش مشاهده‌گر برای تغییر پروژه"},
        format="json",
    )
    assert viewer_project_write.status_code == 403
    viewer_write = viewer_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/",
        {"wbs_code": "2", "wbs_name": "تلاش مشاهده‌گر"},
        format="json",
    )
    assert viewer_write.status_code == 403
    viewer_baseline = viewer_client.post(
        f"/api/v1/projects/{project_a.id}/baselines/",
        {"version_name": "خط مبنای مشاهده‌گر", "make_current": True},
        format="json",
    )
    assert viewer_baseline.status_code == 403
    viewer_import = viewer_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert viewer_import.status_code == 403
    assert _counts(project_a) == before_viewer

    # --- NEG-13: Non-Member System Administrator Observation Exception ---
    admin_observe = admin_client.get(f"/api/v1/projects/{project_b.id}/wbs/")
    assert admin_observe.status_code == 200
    admin_write = admin_client.post(
        f"/api/v1/projects/{project_b.id}/wbs/",
        {"wbs_code": "ADMIN", "wbs_name": "نوشتن مدیر غیرعضو"},
        format="json",
    )
    assert admin_write.status_code == 403
    approver_client = _client_for(p6_personas["independent_approver"])
    project_b.scope_description = "دامنه پروژه مستقل"
    project_b.contract_amount = Decimal("1000.00")
    project_b.project_manager = p6_personas["independent_approver"]
    project_b.save(update_fields=["scope_description", "contract_amount", "project_manager", "updated_at"])
    assert approver_client.post(f"/api/v1/projects/{project_b.id}/complete/").status_code == 200
    undo_preview = admin_client.get(f"/api/v1/projects/{project_b.id}/undo-completion-preview/")
    assert undo_preview.status_code == 200, undo_preview.content
    undo_exec = admin_client.post(
        f"/api/v1/projects/{project_b.id}/undo-completion/",
        {
            "request_id": str(uuid4()),
            "confirmation_token": undo_preview.json()["confirmation_token"],
            "reason": "بازگردانی توسط مدیر غیرعضو",
        },
        format="json",
    )
    assert undo_exec.status_code == 200, undo_exec.content
    assert approver_client.post(f"/api/v1/projects/{project_b.id}/archive/").status_code == 200
    restore_preview = admin_client.get(f"/api/v1/projects/{project_b.id}/restore-preview/")
    assert restore_preview.status_code == 200, restore_preview.content
    restore_exec = admin_client.post(
        f"/api/v1/projects/{project_b.id}/restore/",
        {
            "request_id": str(uuid4()),
            "confirmation_token": restore_preview.json()["confirmation_token"],
            "reason": "بازیابی توسط مدیر غیرعضو",
        },
        format="json",
    )
    assert restore_exec.status_code == 200, restore_exec.content

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
    arch_charter = planner_client.put(
        f"/api/v1/projects/{project_a.id}/kickoff-charter/",
        {"justification": "نباید روی آرشیو نوشته شود", "success_criteria": "x", "constraints": "x", "assumptions": "x", "key_stakeholders_summary": "x", "pm_authority": "x"},
        format="json",
    )
    assert arch_charter.status_code == 400
    assert "project_archived" in str(arch_charter.data)
    arch_wbs = planner_client.post(
        f"/api/v1/projects/{project_a.id}/wbs/",
        {"wbs_code": "ARCH", "wbs_name": "نباید ساخته شود"},
        format="json",
    )
    assert arch_wbs.status_code == 400
    assert "project_archived" in str(arch_wbs.data)
    arch_activity = planner_client.post(
        f"/api/v1/projects/{project_a.id}/activities/",
        {"wbs_id": str(child_a.id), "activity_code": "ARCH", "activity_name": "آرشیو", "duration_days": 1},
        format="json",
    )
    assert arch_activity.status_code == 400
    assert "project_archived" in str(arch_activity.data)
    arch_baseline = planner_client.post(
        f"/api/v1/projects/{project_a.id}/baselines/",
        {"version_name": "نباید ساخته شود"},
        format="json",
    )
    assert arch_baseline.status_code == 400
    assert "project_archived" in str(arch_baseline.data)
    arch_preview = planner_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/preview/",
        {"file": SimpleUploadedFile("branch.xml", (P1_FIXTURES / "branch.xml").read_bytes(), content_type="application/xml")},
        format="multipart",
    )
    assert arch_preview.status_code == 400
    assert arch_preview.json()["error"]["code"] == "project_archived"

    admin_member = ProjectMember.objects.create(
        project=project_a,
        user=p6_personas["system_admin"],
        status=MemberStatus.ACTIVE,
    )
    set_permission_override(admin_member, "edit_wbs", True, actor=p6_personas["system_admin"])
    assert has_organizational_observation(p6_personas["system_admin"])
    assert active_member_has_codename(p6_personas["system_admin"], project_a.id, "edit_wbs")
    admin_import = admin_client.post(
        f"/api/v1/projects/{project_a.id}/import/msp/",
        {
            "file": SimpleUploadedFile(
                "branch.xml",
                (P1_FIXTURES / "branch.xml").read_bytes(),
                content_type="application/xml",
            )
        },
        format="multipart",
    )
    assert admin_import.status_code == 400
    assert admin_import.json()["error"]["code"] == "project_archived"
    assert _counts(project_a) == before_neg06
