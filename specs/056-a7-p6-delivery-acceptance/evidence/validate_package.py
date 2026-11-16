#!/usr/bin/env python3
"""Deterministic delivery package validator for A.7-P6 (056-a7-p6-delivery-acceptance)."""

from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
import xml.etree.ElementTree as ET
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
    pkg: dict = {}
    buckets: dict = {}
    bucket_ids: list[str] = []
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
            else:
                bucket_ids.extend(buckets[bkey])
        if len(bucket_ids) != len(set(bucket_ids)):
            errors.append("summary_buckets overlap: an audit id appears in more than one bucket")

    # 6. Validate 56 AuditDispositionRecord items (audit-disposition.json)
    req_data = json.loads(REQUIREMENTS_JSON.read_text(encoding="utf-8"))
    req_rows = req_data.get("requirements") or req_data.get("items") or []
    original_rows = {row['id']: row for row in req_rows}
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
                original = original_rows.get(aid, {})
                for key, source_key in [('title', 'title'), ('source_requirement', 'requirements'), ('source_acceptance', 'acceptance')]:
                    if row.get(key) != original.get(source_key):
                        errors.append(f"{aid}: {key} differs from the original audit")
                if row.get('version_id') != pkg.get('version_id'):
                    errors.append(f"{aid}: version does not match package")
                if pkg.get('technical_readiness') == 'ready_for_acceptance' and row.get('disposition') != 'تأیید فنی':
                    errors.append(f"{aid}: unresolved disposition in a ready package")
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
            if set(bucket_ids) != expected_audit_ids:
                errors.append(
                    "summary_buckets must partition all 56 audit ids: "
                    f"missing={sorted(expected_audit_ids - set(bucket_ids))}, "
                    f"extra={sorted(set(bucket_ids) - expected_audit_ids)}"
                )
            open_ids = set(buckets.get("still_open_or_unrun") or [])
            if pkg.get("technical_readiness") == "ready_for_acceptance" and open_ids:
                errors.append("technical_readiness cannot be ready_for_acceptance while still_open_or_unrun is non-empty")

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
                if sc.get('version_id') != pkg.get('version_id'):
                    errors.append(f"{sid}: version does not match package")
                if not set(sc.get('audit_ids', [])) <= expected_audit_ids:
                    errors.append(f"{sid}: unknown audit IDs")
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
                if (
                    pkg.get("technical_readiness") == "ready_for_acceptance"
                    and sc.get("technical_result") != "pass"
                ):
                    errors.append(
                        f"{sid}: technical_result is {sc.get('technical_result')} "
                        "(ready_for_acceptance requires pass)"
                    )
                if sc.get("employer_result") not in VALID_EMPLOYER_RESULTS or sc.get("employer_result") != "pending":
                    errors.append(f"{sid}: employer_result must be 'pending', got {sc.get('employer_result')}")
                if sc.get("technical_result") == "pass" and sc.get("defect_id") is not None:
                    errors.append(f"{sid}: defect_id must be null when technical_result == 'pass'")
            if seen_sids != expected_sids:
                errors.append(f"Scenario ID mismatch: missing={expected_sids - seen_sids}")
            if len(seen_sids) != len(scenarios):
                errors.append('Duplicate scenario IDs')

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

    # 9. Ready means actual reports for this immutable source, not just labels.
    verification_path = EVIDENCE_DIR / 'release-verification.json'
    if pkg.get('technical_readiness') == 'ready_for_acceptance':
        if not verification_path.exists():
            errors.append('Ready package lacks release-verification.json')
        else:
            verification = json.loads(verification_path.read_text())
            source = pkg.get('source_commit', '')
            if not re.fullmatch(r'[0-9a-f]{40}', source) or source != pkg.get('git_head') or source != pkg.get('version_id'):
                errors.append('Source/version identity is not an immutable Git commit')
            if verification.get('source_commit') != source or verification.get('image_digest') != pkg.get('acceptance_image_digest'):
                errors.append('Verification source/image differs from package')
            commit = subprocess.run(['git', 'cat-file', '-t', source], cwd=REPO_ROOT, capture_output=True, text=True)
            if commit.returncode or commit.stdout.strip() != 'commit':
                errors.append('Source commit is unavailable')
            scopes = ['apps/api', 'apps/web', 'e2e', 'ops/a7-p5', 'package.json', 'pnpm-lock.yaml', 'pnpm-workspace.yaml', '.npmrc', '.dockerignore']
            listing = subprocess.run(['git', 'ls-tree', '-rz', source, '--', *scopes], cwd=REPO_ROOT, capture_output=True)
            git_blobs = {}
            for entry in listing.stdout.split(b'\0'):
                if entry:
                    metadata, name = entry.split(b'\t', 1)
                    mode, kind, oid = metadata.split()
                    if kind == b'blob':
                        git_blobs[name.decode()] = oid.decode()
            if set(git_blobs) != set(verification.get('source_files_sha256', {})):
                errors.append('Source manifest does not cover the complete candidate source tree')
            for name, digest in verification.get('source_files_sha256', {}).items():
                path = REPO_ROOT / name
                if not path.is_file() or sha256_file(path) != digest:
                    errors.append(f'Source drift after verification: {name}')
                elif hashlib.sha1(b'blob ' + str(path.stat().st_size).encode() + b'\0' + path.read_bytes()).hexdigest() != git_blobs.get(name):
                    errors.append(f'Source differs from immutable candidate: {name}')
            if not verification.get('source_files_sha256'):
                errors.append('Empty source manifest')
            required = {'core', 'host', 'browser_general', 'browser_recovery', 'browser_viewer', 'browser_retry', 'web', 'runtime', 'broker', 'concurrent', 'fresh_start'}
            checks = verification.get('checks', {})
            if set(checks) != required:
                errors.append('Final verification report set is incomplete')
            for name, check in checks.items():
                path = REPO_ROOT / check.get('path', '')
                if not path.is_file() or sha256_file(path) != check.get('sha256'):
                    errors.append(f'{name}: missing or changed final report')
                    continue
                if check.get('kind') == 'junit':
                    root = ET.parse(path).getroot()
                    cases = root.findall('.//testcase')
                    if not cases or any(c.find(tag) is not None for c in cases for tag in ['failure', 'error', 'skipped']):
                        errors.append(f'{name}: final JUnit did not pass without skips')
                    if len(cases) < {'core': 722, 'host': 110}.get(name, 1):
                        errors.append(f'{name}: final JUnit scope is incomplete')
                elif check.get('kind') == 'playwright':
                    stats = json.loads(path.read_text()).get('stats', {})
                    if not stats.get('expected') or any(stats.get(k, 0) for k in ['unexpected', 'skipped', 'flaky']):
                        errors.append(f'{name}: final browser run did not pass')
                    if stats.get('expected') != {'browser_general': 20, 'browser_recovery': 3, 'browser_viewer': 2, 'browser_retry': 4}.get(name):
                        errors.append(f'{name}: final browser scope is incomplete')
                else:
                    report = json.loads(path.read_text())
                    if name == 'runtime':
                        if report.get('status') != 'ready' or report.get('not_run') or not report.get('matrix') or any(v != 'pass' for v in report['matrix'].values()):
                            errors.append('Final real-worker matrix did not fully pass')
                        local_hash = hashlib.sha256(b''.join(p.read_bytes() for p in sorted((REPO_ROOT / 'apps/api/core/schedule').rglob('*.py')))).hexdigest()
                        if report.get('source_tree_sha256') != pkg.get('schedule_tree_sha256') or local_hash != pkg.get('schedule_tree_sha256'):
                            errors.append('Runtime matrix has a stale schedule-tree digest')
                    elif report.get('status') != 'pass':
                        errors.append(f'{name}: final report did not pass')
                    elif name == 'web':
                        if report.get('source_commit') != source or report.get('api_image_digest') != pkg.get('acceptance_image_digest') or report.get('web_image_digest') != pkg.get('web_image_digest'):
                            errors.append('Compiled web/API verification has a different candidate identity')
                    elif name == 'fresh_start':
                        if report.get('api_image_digest') != pkg.get('acceptance_image_digest') or not report.get('separate_network_verified') or not report.get('disposable_stack_removed'):
                            errors.append('Fresh installation is unverified or left disposable resources')

    # 10. Secret scan across all P6 markdown and json files
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
                "technical_readiness": pkg.get("technical_readiness"),
                "employer_decision": "pending",
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
