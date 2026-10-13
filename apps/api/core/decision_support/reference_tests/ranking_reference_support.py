"""Test-local observations; never imported by production calculations."""

from copy import deepcopy
from pathlib import Path
from datetime import datetime, timedelta
import ast
import hashlib
import io
import re
import zipfile
import xml.etree.ElementTree as ET
from ranking_reference_fixtures import DOCX_PATH, MARKDOWN_PATH, DOCX_SHA, SOURCE_SHA, BLOCK_SHA, FIELDS

def observe(function, inputs):
    copied = deepcopy(inputs)
    before = deepcopy(copied)
    observation = {"inputs": deepcopy(inputs), "value": None, "error_class": None}
    try:
        observation["value"] = deepcopy(function(*copied))
    except Exception as error:
        observation.update(error_class=type(error).__name__, error_message=str(error),
                           error_details=deepcopy(getattr(error, "detail", None)))
    observation["input_unchanged"] = copied == before
    return observation



ROOT = Path(__file__).resolve().parents[5]


def digest(value):
    return hashlib.sha256(value).hexdigest()


def validate_shape(source):
    try:
        tree = ast.parse(source)
    except SyntaxError as error:
        raise ValueError("Invalid reference syntax") from error
    if len(tree.body) != 2:
        raise ValueError("Expected one import and one function")
    imported, function = tree.body
    if not (isinstance(imported, ast.ImportFrom) and imported.module == "math" and imported.level == 0
            and [(x.name, x.asname) for x in imported.names] == [("isfinite", None), ("sqrt", None)]):
        raise ValueError("Unexpected reference import")
    if not (isinstance(function, ast.FunctionDef) and function.name == "rank_options"
            and tuple(x.arg for x in function.args.args) == FIELDS and not function.decorator_list
            and not function.args.posonlyargs and not function.args.vararg and not function.args.kwarg
            and not function.args.kwonlyargs and not function.args.defaults and not function.returns
            and not any(x.annotation for x in function.args.args)):
        raise ValueError("Unexpected reference callable")
    if any(isinstance(node, (ast.Import, ast.ImportFrom)) for node in ast.walk(function)):
        raise ValueError("Unexpected nested import")


def authenticate(markdown, docx_bytes):
    if digest(docx_bytes) != DOCX_SHA:
        raise ValueError("Original DOCX identity changed")
    blocks = re.findall(r"```python\n(.*?)\n```", markdown, re.S)
    implementations = [block for block in blocks if block.startswith("from math import isfinite, sqrt\n")
                       and "def rank_options(" in block]
    if len(implementations) != 1:
        raise ValueError("Expected a unique implementation fence")
    source = implementations[0]
    if digest(source.encode()) != SOURCE_SHA or digest((source + "\n").encode()) != BLOCK_SHA:
        raise ValueError("Preserved reference text changed")
    with zipfile.ZipFile(io.BytesIO(docx_bytes)) as archive:
        document = ET.fromstring(archive.read("word/document.xml"))
    ns = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}
    paragraphs = []
    for paragraph in document.findall(".//w:p", ns):
        parts = []
        for node in paragraph.iter():
            tag = node.tag.rsplit("}", 1)[-1]
            if tag == "t":
                parts.append(node.text or "")
            elif tag in ("br", "cr"):
                parts.append("\n")
            elif tag == "tab":
                parts.append("\t")
        text = "".join(parts)
        if text.startswith("from math import isfinite, sqrt"):
            paragraphs.append(text)
    if paragraphs != [source]:
        raise ValueError("Markdown and original DOCX sample differ")
    validate_shape(source)
    return source


def reference():
    source = authenticate((ROOT / MARKDOWN_PATH).read_text(), (ROOT / DOCX_PATH).read_bytes())
    namespace = {}
    exec(compile(source, MARKDOWN_PATH, "exec"), namespace)
    return namespace["rank_options"]


def compare(rows, score_field, names, scores, order):
    import math
    assert isinstance(rows, list), "Ranking must be a list"
    assert len(rows) == len(names), "Missing/extra alternative"
    assert len(names) == len(set(names)), "Fixture names must be unique"
    assert len(scores) == len(names), "Expected score count mismatch"
    assert all(isinstance(row, dict) and isinstance(row.get("option"), str)
               and score_field in row for row in rows), "Invalid ranking row"
    identities = [row["option"] for row in rows]
    assert len(set(identities)) == len(names) and set(identities) == set(names), "Alternative membership changed"
    assert identities == order, "Exact alternative order changed"
    for row in rows:
        score = row[score_field]
        assert isinstance(score, (int, float)) and not isinstance(score, bool) and math.isfinite(score), "Non-finite/nonnumeric score"
        expected = scores[names.index(row["option"])]
        assert math.isfinite(expected) and abs(score - expected) <= 1e-9, "Score exceeds absolute tolerance"
    return True


def check_rejection(observation, source, issue=None, method=None):
    assert observation.get("input_unchanged", True), "Rejected call mutated inputs"
    if source == "reference":
        assert observation.get("error_class") in ("ValueError", "TypeError"), "Expected reference rejection"
    else:
        assert source == "product" and observation.get("error_class") == "CodedValidationError", "Expected located product rejection"
        assert isinstance(issue, dict), "Expected product issue required"
        expected = dict(issue)
        if method == "TOPSIS" and expected["code"] == "benefit_column_all_zero":
            expected["code"] = "topsis_denom_zero"
        details = observation.get("error_details")
        assert isinstance(details, dict) and isinstance(details.get("issues"), list), "Missing product issues"
        assert any(isinstance(actual, dict) and actual.get("path") == expected["path"]
                   and actual.get("code") == expected["code"] for actual in details["issues"]), "Wrong product issue/path"
    return True


def has_observations(observations):
    """Pytest lifecycle bookkeeping cannot stand in for observed behavior."""
    return isinstance(observations, dict) and (
        bool(observations.get("helper_events"))
        or any(key not in ("helper_events", "pytest") for key in observations)
    )


def build_report(required, records, phases, metadata, exit_status):
    checks = []
    for key, descriptor in required.items():
        observed = records.get(key, {})
        outcomes = phases.get(key, {})
        if "failed" in outcomes.values():
            status = "failed"
        elif (all(outcomes.get(phase) == "passed" for phase in ("setup", "call", "teardown"))
              and has_observations(observed.get("observations"))):
            status = "passed"
        else:
            status = "unrun"
        checks.append({"id": key, **descriptor, **observed, "observations": observed.get("observations"), "phases": outcomes, "status": status,
                       "reason": "Assertions and all phases passed" if status == "passed" else "Failed or incomplete observation/phases"})
    return {"schema_version": 1, **metadata, "exit_status": int(exit_status), "required_check_ids": list(required), "checks": checks,
            "complete": bool(checks) and exit_status == 0 and all(c["status"] == "passed" for c in checks)}


def json_safe(value):
    import math
    if isinstance(value, float) and not math.isfinite(value):
        return {"kind": "non-finite", "value": "NaN" if math.isnan(value) else "+Infinity" if value > 0 else "-Infinity"}
    if value is None or isinstance(value, (str, bool, int, float)):
        return value
    if isinstance(value, dict):
        return {str(key): json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)):
        return [json_safe(item) for item in value]
    if isinstance(value, bytes):
        return {"kind": "bytes", "sha256": digest(value), "length": len(value)}
    if isinstance(value, Path):
        return str(value)
    if callable(value):
        return {"kind": "callable", "name": value.__name__}
    raise TypeError("Unsupported evidence value: " + type(value).__name__)


def strict_json(value):
    import json
    return json.dumps(json_safe(value), ensure_ascii=False, allow_nan=False, indent=2)


def _validate_provenance(report):
    def sha(value, lengths):
        return isinstance(value, str) and len(value) in lengths and re.fullmatch(r"[0-9a-f]+", value)

    try:
        stamp = datetime.fromisoformat(report["generated_at"])
        utc = stamp.tzinfo is not None and stamp.utcoffset() == timedelta(0)
    except (KeyError, TypeError, ValueError):
        utc = False
    if not utc or not sha(report.get("git_sha"), (40, 64)):
        raise ValueError("Missing/malformed UTC time or Git identity")
    hashes = report.get("source_hashes")
    if not (isinstance(hashes, dict) and hashes and all(
            isinstance(path, str) and path and not Path(path).is_absolute() and ".." not in Path(path).parts
            and sha(value, (64,)) for path, value in hashes.items())):
        raise ValueError("Missing/malformed relevant source hashes")
    identity = report.get("reference_identity")
    if not (isinstance(identity, dict) and all(identity.get(key) == value for key, value in (
            ("docx_sha256", DOCX_SHA), ("source_sha256", SOURCE_SHA), ("block_sha256", BLOCK_SHA)))):
        raise ValueError("Missing/malformed pinned reference identity")
    versions = report.get("versions")
    if not (isinstance(versions, dict) and all(isinstance(versions.get(key), str) and versions[key].strip()
            for key in ("python", "django", "drf", "pytest"))):
        raise ValueError("Missing/malformed tool versions")
    command = report.get("command")
    if not (isinstance(command, list) and command and all(isinstance(arg, str) and arg.strip() for arg in command)
            and report.get("cwd") == "apps/api/core"):
        raise ValueError("Missing/malformed command or working directory")
    if report.get("evidence_level") != "arithmetic" or report.get("product_browser_acceptance") is not False:
        raise ValueError("Invalid reference evidence boundary")


def read_report(path):
    import json
    def reject_constant(value):
        raise ValueError("Invalid JSON constant: " + value)
    report = json.loads(Path(path).read_text(), parse_constant=reject_constant)
    if not (isinstance(report, dict) and type(report.get("schema_version")) is int and report["schema_version"] == 1
            and isinstance(report.get("checks"), list) and report["checks"]
            and isinstance(report.get("required_check_ids"), list)
            and type(report.get("exit_status")) is int and isinstance(report.get("complete"), bool)):
        raise ValueError("Incomplete report envelope")
    _validate_provenance(report)
    ids = []
    for check in report["checks"]:
        if not (isinstance(check, dict) and isinstance(check.get("id"), str)
                and check.get("status") in ("passed", "failed", "unrun")
                and check.get("evidence_level") == "arithmetic"
                and "expected" in check and "observations" in check and "phases" in check):
            raise ValueError("Incomplete check")
        ids.append(check["id"])
        outcomes = check["phases"]
        if not isinstance(outcomes, dict):
            raise ValueError("Invalid phase record")
        if check["status"] == "passed" and (set(outcomes) != {"setup", "call", "teardown"} or not has_observations(check["observations"]) or
                not all(outcomes.get(p) == "passed" for p in ("setup", "call", "teardown"))):
            raise ValueError("Invalid passing status")
    if len(ids) != len(set(ids)) or ids != report["required_check_ids"]:
        raise ValueError("Missing/duplicate required check identity")
    complete = report["exit_status"] == 0 and all(c["status"] == "passed" for c in report["checks"])
    if report["complete"] != complete:
        raise ValueError("Dishonest completeness")
    return report
