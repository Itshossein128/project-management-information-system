#!/usr/bin/env python3
"""Deterministic delivery package validator for A.7-P6 (056-a7-p6-delivery-acceptance)."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
FEATURE_DIR = REPO_ROOT / "specs" / "056-a7-p6-delivery-acceptance"
EVIDENCE_DIR = FEATURE_DIR / "evidence"
REQUIREMENTS_JSON = REPO_ROOT / "output" / "a7-requirements-2026-11-10" / "requirements.json"
PHASE_MAP_JSON = REPO_ROOT / "output" / "a7-implementation" / "phase-map.json"
PLAN_MPP = REPO_ROOT / "real-data" / "plan.mpp"

AUDIT_ID_RE = re.compile(r"^(P0[1-9]|P1[01]|W0[1-7]|M0[1-4]|S0[1-8]|I0[1-9]|I1[0-9]|I2[0-2]|D0[1-4])$")
SCENARIO_ID_RE = re.compile(r"^(POS-(0[1-9]|10)|NEG-(0[1-9]|1[0-4])|OPS-0[1-4])$")

VALID_PHASES = {"A.7-P1", "A.7-P2", "A.7-P3", "A.7-P4", "A.7-P5", "A.7-P6"}
VALID_DISPOSITIONS = {"تأیید فنی", "ناقص", "اجرانشده", "نیازمند پاسخ کارفرما"}
VALID_EMPLOYER_BUCKETS = {
    "قبلاً موجود و تأییدشده روی نسخه حاضر",
    "در A.7 اصلاح/تکمیل شد",
    "هنوز باز/اجرانشده",
    "قابل تست توسط کارفرما",
}
VALID_CATEGORIES = {"positive", "negative", "concurrency", "access_boundary", "bilingual_ux", "operational"}
VALID_PERSONAS = {
    "creator_planner",
    "independent_approver",
    "viewer",
    "system_admin",
    "org_reference_steward",
    "multi_role",
}
VALID_CHANNELS = {"api_db", "real_worker", "browser_e2e", "combined"}
VALID_TECH_RESULTS = {"pass", "fail", "not_run"}
VALID_EMPLOYER_RESULTS = {"pending", "accepted", "rejected"}
VALID_FIXTURES = {"real_data_plan_mpp", "valid_msp_xml", "valid_p6_xer", "valid_p6_xml"}

SECRET_PATTERNS = [
    re.compile(r"devpass123", re.IGNORECASE),
    re.compile(r"Bearer\s+[A-Za-z0-9_\-\.]{20,}"),
    re.compile(r"eyJ[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}\.[A-Za-z0-9_\-]{10,}"),
]


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []

    # 1. Verify requirements.json is untouched in git
    git_diff = subprocess.run(
        ["git", "status", "--porcelain", "output/a7-requirements-2026-11-10/"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
        check=False,
    )
    if git_diff.stdout.strip():
        errors.append(f"Historical audit snapshot modified: {git_diff.stdout.strip()}")

    # 2. Verify phase-map.json preserves all 6 phases
    if not PHASE_MAP_JSON.exists():
        errors.append("Missing output/a7-implementation/phase-map.json")
    else:
        phase_map = json.loads(PHASE_MAP_JSON.read_text(encoding="utf-8"))
        expected_keys = {
            "a7-p1-project-reference",
            "a7-p2-import-safety",
            "a7-p3-import-fidelity",
            "a7-p4-import-experience",
            "a7-p5-import-operations",
            "a7-p6-delivery-acceptance",
        }
        if set(phase_map.keys()) != expected_keys:
            errors.append(f"phase-map.json keys mismatch: {set(phase_map.keys())} != {expected_keys}")
        for key, entry in phase_map.items():
            fdir = REPO_ROOT / entry["feature_directory"]
            for req_file in ["spec.md", "handoff.md", "traceability.md", "evidence/verification.md"]:
                if not (fdir / req_file).exists():
                    errors.append(f"Missing {req_file} in {entry['feature_directory']} ({key})")

    # 3. Verify real-data/plan.mpp fingerprint
    if not PLAN_MPP.exists():
        errors.append("Missing real-data/plan.mpp")
    else:
        digest = sha256_file(PLAN_MPP)
        size = PLAN_MPP.stat().st_size
        if digest != "3a4f800f0f57e408be52095117f1a53887f653ac07f720621b3e22aa67765553" or size != 777216:
            errors.append(f"real-data/plan.mpp fingerprint mismatch: sha256={digest}, size={size}")

    # 4. Verify required P6 files exist
    required_p6_files = [
        FEATURE_DIR / "spec.md",
        FEATURE_DIR / "plan.md",
        FEATURE_DIR / "research.md",
        FEATURE_DIR / "data-model.md",
        FEATURE_DIR / "quickstart.md",
        FEATURE_DIR / "guide.md",
        FEATURE_DIR / "traceability.md",
        FEATURE_DIR / "handoff.md",
        FEATURE_DIR / "contracts" / "delivery-acceptance.md",
        FEATURE_DIR / "checklists" / "requirements.md",
        EVIDENCE_DIR / "package.json",
        EVIDENCE_DIR / "audit-disposition.json",
        EVIDENCE_DIR / "reconciliation.json",
        EVIDENCE_DIR / "reconciliation.md",
        EVIDENCE_DIR / "scenarios.json",
        EVIDENCE_DIR / "scenarios.md",
        EVIDENCE_DIR / "accounts.md",
        EVIDENCE_DIR / "defects.md",
        EVIDENCE_DIR / "minutes.md",
        EVIDENCE_DIR / "verification.md",
    ]
    for p in required_p6_files:
        if not p.exists():
            errors.append(f"Missing required P6 artifact: {p.relative_to(REPO_ROOT)}")

    # 5. Validate EmployerDeliveryPackage (package.json)
    pkg_path = EVIDENCE_DIR / "package.json"
    if pkg_path.exists():
        pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
        if pkg.get("django_version") != "4.2.11":
            errors.append(f"package.json django_version must be 4.2.11, got {pkg.get('django_version')}")
        if pkg.get("technical_readiness") not in {"ready_for_acceptance", "blocked"}:
            errors.append(f"Invalid technical_readiness: {pkg.get('technical_readiness')}")
        if pkg.get("employer_decision") != "pending":
            errors.append(f"Authored employer_decision must be 'pending', got {pkg.get('employer_decision')}")
        if pkg.get("employer_signer_role") != "" or pkg.get("employer_signed_at") != "":
            errors.append("Authored employer_signer_role and employer_signed_at must be empty strings")
        expected_personas = [
            "creator_planner",
            "independent_approver",
            "viewer",
            "system_admin",
            "org_reference_steward",
        ]
        if pkg.get("role_personas") != expected_personas:
            errors.append(f"role_personas mismatch: {pkg.get('role_personas')}")
        buckets = pkg.get("summary_buckets", {})
        for bkey in ["already_verified", "fixed_in_a7", "still_open_or_unrun", "testable_by_employer"]:
            if bkey not in buckets or not isinstance(buckets[bkey], list):
                errors.append(f"Missing or invalid summary_buckets.{bkey}")

    # 6. Validate 56 AuditDispositionRecord items (audit-disposition.json)
    req_data = json.loads(REQUIREMENTS_JSON.read_text(encoding="utf-8"))
    req_rows = req_data.get("requirements") or req_data.get("items") or []
    expected_audit_ids = {item["id"] for item in req_rows}
    disp_path = EVIDENCE_DIR / "audit-disposition.json"
    if disp_path.exists():
        disp_items = json.loads(disp_path.read_text(encoding="utf-8"))
        if not isinstance(disp_items, list) or len(disp_items) != 56:
            errors.append(f"audit-disposition.json must contain 56 items, got {len(disp_items) if isinstance(disp_items, list) else 'non-list'}")
        else:
            seen_ids: set[str] = set()
            for row in disp_items:
                aid = row.get("audit_id", "")
                if not AUDIT_ID_RE.match(aid):
                    errors.append(f"Invalid audit_id format: {aid}")
                seen_ids.add(aid)
                if row.get("owning_phase") not in VALID_PHASES:
                    errors.append(f"{aid}: invalid owning_phase {row.get('owning_phase')}")
                if not row.get("source_requirement"):
                    errors.append(f"{aid}: empty source_requirement")
                if row.get("disposition") not in VALID_DISPOSITIONS:
                    errors.append(f"{aid}: invalid disposition {row.get('disposition')}")
                if row.get("employer_bucket") not in VALID_EMPLOYER_BUCKETS:
                    errors.append(f"{aid}: invalid employer_bucket {row.get('employer_bucket')}")
                ev_refs = row.get("evidence_refs", [])
                if not isinstance(ev_refs, list) or not ev_refs:
                    errors.append(f"{aid}: evidence_refs must be a non-empty list")
                else:
                    for ref in ev_refs:
                        if not (REPO_ROOT / ref).exists():
                            errors.append(f"{aid}: evidence_ref does not exist: {ref}")
                if not row.get("version_id"):
                    errors.append(f"{aid}: missing version_id")
            if seen_ids != expected_audit_ids:
                errors.append(f"Audit ID coverage mismatch: missing={expected_audit_ids - seen_ids}, extra={seen_ids - expected_audit_ids}")

    # 7. Validate 28 AcceptanceScenarioRecord items (scenarios.json)
    scen_path = EVIDENCE_DIR / "scenarios.json"
    if scen_path.exists():
        scenarios = json.loads(scen_path.read_text(encoding="utf-8"))
        expected_sids = (
            {f"POS-{i:02d}" for i in range(1, 11)}
            | {f"NEG-{i:02d}" for i in range(1, 15)}
            | {f"OPS-{i:02d}" for i in range(1, 5)}
        )
        if not isinstance(scenarios, list) or len(scenarios) < 28:
            errors.append(f"scenarios.json must have at least 28 scenarios, got {len(scenarios) if isinstance(scenarios, list) else 'non-list'}")
        else:
            seen_sids: set[str] = set()
            for sc in scenarios:
                sid = sc.get("scenario_id", "")
                if not SCENARIO_ID_RE.match(sid):
                    errors.append(f"Invalid scenario_id: {sid}")
                seen_sids.add(sid)
                if sc.get("category") not in VALID_CATEGORIES:
                    errors.append(f"{sid}: invalid category {sc.get('category')}")
                if not sc.get("audit_ids"):
                    errors.append(f"{sid}: empty audit_ids")
                if sc.get("role_persona") not in VALID_PERSONAS:
                    errors.append(f"{sid}: invalid role_persona {sc.get('role_persona')}")
                if sc.get("channel") not in VALID_CHANNELS:
                    errors.append(f"{sid}: invalid channel {sc.get('channel')}")
                for req_str in ["input_ref", "expected_outcome", "observed_outcome", "evidence_ref"]:
                    if not sc.get(req_str):
                        errors.append(f"{sid}: empty {req_str}")
                if sc.get("evidence_ref") and not (REPO_ROOT / sc["evidence_ref"]).exists():
                    errors.append(f"{sid}: missing evidence_ref file {sc['evidence_ref']}")
                if sc.get("technical_result") not in VALID_TECH_RESULTS:
                    errors.append(f"{sid}: invalid technical_result {sc.get('technical_result')}")
                if sc.get("technical_result") != "pass":
                    errors.append(f"{sid}: technical_result is {sc.get('technical_result')} (expected 'pass' for ready_for_acceptance)")
                if sc.get("employer_result") not in VALID_EMPLOYER_RESULTS or sc.get("employer_result") != "pending":
                    errors.append(f"{sid}: employer_result must be 'pending', got {sc.get('employer_result')}")
                if sc.get("technical_result") == "pass" and sc.get("defect_id") is not None:
                    errors.append(f"{sid}: defect_id must be null when technical_result == 'pass'")
            if seen_sids != expected_sids:
                errors.append(f"Scenario ID mismatch: missing={expected_sids - seen_sids}")

    # 8. Validate ReferenceScheduleReconciliationRecord (reconciliation.json)
    rec_path = EVIDENCE_DIR / "reconciliation.json"
    if rec_path.exists():
        recs = json.loads(rec_path.read_text(encoding="utf-8"))
        seen_fids = {r.get("fixture_id") for r in recs}
        if seen_fids != VALID_FIXTURES:
            errors.append(f"reconciliation.json fixtures mismatch: {seen_fids} != {VALID_FIXTURES}")
        for r in recs:
            fid = r.get("fixture_id")
            fpath = REPO_ROOT / r.get("file_path", "")
            if not fpath.exists():
                errors.append(f"{fid}: missing file_path {r.get('file_path')}")
            else:
                if sha256_file(fpath) != r.get("sha256"):
                    errors.append(f"{fid}: sha256 mismatch")
                if fpath.stat().st_size != r.get("size_bytes"):
                    errors.append(f"{fid}: size_bytes mismatch")
            if fid == "real_data_plan_mpp":
                if r.get("stored_counts") != {"wbs_count": 6, "activity_count": 72, "relation_count": 72}:
                    errors.append(f"real_data_plan_mpp stored_counts mismatch: {r.get('stored_counts')}")
                rep = r.get("repeat_append_result", {})
                if rep != {
                    "nothing_changed": True,
                    "duplicate_wbs": 0,
                    "duplicate_activities": 0,
                    "duplicate_relations": 0,
                    "extra_baselines": 0,
                }:
                    errors.append(f"real_data_plan_mpp repeat_append_result mismatch: {rep}")
                expected_warns = {"activity_without_parent", "predecessor_is_summary", "calendar_not_applied"}
                if set(r.get("expected_warning_codes", [])) != expected_warns:
                    errors.append(f"real_data_plan_mpp expected_warning_codes mismatch: {r.get('expected_warning_codes')}")

    # 9. Secret scan across all P6 markdown and json files
    for p in FEATURE_DIR.rglob("*"):
        if p.is_file() and p.suffix in {".md", ".json"}:
            content = p.read_text(encoding="utf-8")
            for pat in SECRET_PATTERNS:
                if pat.search(content):
                    errors.append(f"Secret pattern '{pat.pattern}' detected in {p.relative_to(REPO_ROOT)}")

    if errors:
        print(json.dumps({"status": "failed", "error_count": len(errors), "errors": errors}, ensure_ascii=False, indent=2))
        return 1

    print(
        json.dumps(
            {
                "status": "passed",
                "audit_items_verified": 56,
                "scenarios_verified": 28,
                "reconciliation_fixtures_verified": 4,
                "secret_scan": "clean",
                "technical_readiness": "ready_for_acceptance",
                "employer_decision": "pending",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
