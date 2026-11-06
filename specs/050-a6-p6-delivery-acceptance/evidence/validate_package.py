"""Validate A6-P6 evidence records and reject secret material without echoing it."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

ALLOWED_RESULTS = {"pass", "fail", "not_run", "not_applicable"}
SECRET = re.compile(
    r"(?i)(?:password|passwd|refresh_token|access_token|reset_token|recovery_link|recovery_url)"
    r"\s*[\"']?\s*[:=]\s*[\"']?[^\s\"',]{3,}"
    r"|bearer\s+[A-Za-z0-9._\-]{8,}"
    r"|[?&](?:token|reset|recovery)=[^&\s]+"
)


def fail(message: str) -> int:
    print(message, file=sys.stderr)
    return 1


def check_payload(payload: dict) -> str | None:
    result = payload.get("result")
    if result not in ALLOWED_RESULTS:
        return f"result must be pass, fail, not_run, or not_applicable; got {result!r}"
    if result == "not_applicable" and not str(payload.get("na_reason") or "").strip():
        return "na_reason is required when result is not_applicable"
    if result == "fail" and not str(payload.get("defect_id") or "").strip():
        return "fail cites a defect"
    rollup = str(payload.get("rollup") or "")
    if result == "not_run" and rollup == "pass":
        return "not_run is not a pass"
    return None


def check_text(path: Path, text: str) -> str | None:
    if SECRET.search(text):
        return f"secret pattern matched in {path}; value omitted"
    return None


def _cells(line: str) -> list[str]:
    return [part.strip() for part in line.strip().strip("|").split("|")]


def check_markdown_tables(path: Path, text: str) -> list[str]:
    errors: list[str] = []
    lines = text.splitlines()
    header: list[str] | None = None
    for line in lines:
        if not line.startswith("|"):
            header = None
            continue
        cells = _cells(line)
        if set(cells) <= {"---", ":---", "---:", ":---:"} or all(set(cell) <= {"-", ":"} for cell in cells):
            continue
        if header is None:
            header = [cell.lower() for cell in cells]
            continue
        row = dict(zip(header, cells))
        for key in ("result", "technical_result"):
            if key not in row:
                continue
            value = row[key].strip("`")
            if value not in ALLOWED_RESULTS:
                errors.append(f"{path}: {key} must be pass, fail, not_run, or not_applicable")
            if value == "not_applicable" and not row.get("na_reason", "").strip("` ").strip():
                errors.append(f"{path}: na_reason is required when result is not_applicable")
            if value == "fail" and not row.get("defect_id", "").strip("` ").strip():
                errors.append(f"{path}: fail cites a defect")
            if value == "not_run" and row.get("rollup", "").strip("`") == "pass":
                errors.append(f"{path}: not_run is not a pass")
    return errors


def scan_file(path: Path) -> list[str]:
    text = path.read_text()
    errors: list[str] = []
    secret = check_text(path, text)
    if secret:
        errors.append(secret)
    if path.suffix == ".json":
        problem = check_payload(json.loads(text))
        if problem:
            errors.append(f"{path}: {problem}")
    if path.suffix == ".md":
        errors.extend(check_markdown_tables(path, text))
    return errors


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        return fail("usage: validate_package.py <file-or-directory>")
    target = Path(argv[1])
    if target.is_file():
        errors = scan_file(target)
        return fail("\n".join(errors)) if errors else 0
    if not target.is_dir():
        return fail(f"not a file or directory: {target}")
    errors: list[str] = []
    files = [path for path in sorted(target.rglob("*")) if path.is_file() and "fixtures" not in path.parts]
    guide = target.parent / "guide.md"
    if guide.is_file():
        files.append(guide)
    for path in files:
        if path.suffix not in {".md", ".json"}:
            continue
        errors.extend(scan_file(path))
    if errors:
        return fail("\n".join(errors))
    print("package evidence accepted")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
