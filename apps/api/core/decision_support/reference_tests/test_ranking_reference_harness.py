
import pytest
from django.db import connection
from ranking_reference_support import observe
from ranking_reference_fixtures import DOCX_PATH, MARKDOWN_PATH, DOCX_SHA, SOURCE_SHA, BLOCK_SHA
from ranking_reference_support import ROOT, authenticate, validate_shape
from ranking_reference_support import compare
from ranking_reference_support import check_rejection
import json
import importlib.util
from types import SimpleNamespace
from ranking_reference_support import build_report, strict_json, read_report


def _report_metadata():
    """Explicit synthetic provenance for reader contract tests, not product evidence."""
    return {"generated_at": "2026-10-13T00:00:00+00:00", "git_sha": "a" * 40,
            "source_hashes": {"synthetic/fixture.py": "b" * 64},
            "reference_identity": {"docx_sha256": DOCX_SHA, "source_sha256": SOURCE_SHA, "block_sha256": BLOCK_SHA},
            "versions": {"python": "3.12.3", "django": "4.2.11", "drf": "3.17.1", "pytest": "9.1.1"},
            "command": ["python", "-m", "pytest", "synthetic-reader-probe"],
            "cwd": "apps/api/core", "evidence_level": "arithmetic", "product_browser_acceptance": False}


def _reader_report(partial=False):
    required = {key: {"expected": i, "evidence_level": "arithmetic"} for i, key in enumerate(("a", "b"), 1)}
    keys = ["a"] if partial else ["a", "b"]
    return build_report(required, {key: {"observations": {"actual": required[key]["expected"]}} for key in keys},
                        {key: {p: "passed" for p in ("setup", "call", "teardown")} for key in keys}, _report_metadata(), 0)

def test_observation_copies_inputs():
    inputs = [[1], [2]]
    def mutate(a, b):
        a.append(9)
        return [a, b]
    observed = observe(mutate, inputs)
    assert inputs == [[1], [2]]
    assert observed["input_unchanged"] is False
    assert observed["value"] == [[1, 9], [2]]


def test_observation_retains_error():
    def fail(value):
        raise ValueError("deliberate rejection")
    observed = observe(fail, [[1]])
    assert observed["error_class"] == "ValueError"
    assert observed["error_message"] == "deliberate rejection"
    assert observed["input_unchanged"] is True


def test_reference_database_is_blocked(record):
    observed = observe(lambda: connection.cursor(), [])
    record({"id": "database-blocker", "inputs": {"operation": "connection.cursor"}},
           {"database": observed}, {"error_class": "RuntimeError", "message": "Database access not allowed"})
    assert observed["error_class"] == "RuntimeError"
    assert "Database access not allowed" in observed["error_message"]



@pytest.mark.parametrize("mutation", ["message", "comment", "whitespace", "missing", "duplicate", "source"])
def test_counterfeit_reference_rejected(mutation):
    markdown = (ROOT / MARKDOWN_PATH).read_text()
    docx = (ROOT / DOCX_PATH).read_bytes()
    if mutation == "message":
        markdown = markdown.replace("نام معیار یا گزینه نمی‌تواند خالی باشد.", "changed error")
    elif mutation == "comment":
        markdown = markdown.replace("# SAW:", "# modified SAW:")
    elif mutation == "whitespace":
        markdown = markdown.replace("    m, n =", "     m, n =")
    elif mutation == "missing":
        markdown = markdown.replace("from math import isfinite, sqrt", "# missing implementation")
    elif mutation == "duplicate":
        markdown += "\n" + markdown
    else:
        docx += b"changed source archive"
    with pytest.raises(ValueError):
        authenticate(markdown, docx)


@pytest.mark.parametrize("source", [
    "import os\ndef rank_options(a,b,c,d,e): pass",
    "from math import isfinite, sqrt\ndef rank_options(a): pass",
    "from math import isfinite, sqrt\ndef wrong(a,b,c,d,e): pass",
    "from math import isfinite, sqrt\n@decorator\ndef rank_options(criteria, alternatives, weights, types, matrix): pass",
    "from math import isfinite, sqrt\ndef rank_options(criteria, alternatives, weights, types, matrix): pass\nprint('extra')",
])
def test_wrong_shape_rejected(source):
    with pytest.raises(ValueError):
        validate_shape(source)



@pytest.mark.parametrize("rows", [
    [{"option":"A","score":1.00001},{"option":"B","score":.5}],
    [{"option":"A","score":float("nan")},{"option":"B","score":.5}],
    [{"option":"A","score":float("inf")},{"option":"B","score":.5}],
    [{"option":"A","score":1}],
    [{"option":"A","score":1},{"option":"A","score":.5}],
    [{"option":"Changed","score":1},{"option":"B","score":.5}],
    [{"option":"B","score":.5},{"option":"A","score":1}],
    [{"option":"A","TOPSIS":1},{"option":"B","TOPSIS":.5}],
    [{"option":"A","score":True},{"option":"B","score":.5}],
    None, [None],
])
def test_bad_result_rejected(rows):
    with pytest.raises(AssertionError):
        compare(rows,"score",["A","B"],[1,.5],["A","B"])


def test_tie_order_is_exact():
    with pytest.raises(AssertionError):
        compare([{"option":"B","score":1},{"option":"A","score":1}], "score", ["A","B"],[1,1],["A","B"])


def test_absolute_tolerance_boundary():
    assert compare([{"option":"A","score":1e-9}],"score",["A"],[0],["A"])
    with pytest.raises(AssertionError):
        compare([{"option":"A","score":1.0001e-9}],"score",["A"],[0],["A"])



@pytest.mark.parametrize("observation,source,issue", [
    ({"error_class":None,"value":{}},"reference",None),
    ({"error_class":"KeyError"},"reference",None),
    ({"error_class":"ValueError"},"product",{"code":"cost_zero","path":"performance_matrix.0.0"}),
    ({"error_class":"CodedValidationError","error_details":{"issues":[{"code":"cost_zero","path":"wrong"}]}},"product",{"code":"cost_zero","path":"performance_matrix.0.0"}),
    ({"error_class":"CodedValidationError","error_details":{"issues":[]}},"product",{"code":"cost_zero","path":"performance_matrix.0.0"}),
])
def test_wrong_rejection_fails(observation,source,issue):
    with pytest.raises(AssertionError):
        check_rejection(observation,source,issue,"SAW")



@pytest.mark.parametrize("bad_phase",["setup","call","teardown"])
def test_failed_phase_cannot_pass(bad_phase):
    phases={"a":{"setup":"passed","call":"passed","teardown":"passed"}}
    phases["a"][bad_phase]="failed"
    report=build_report({"a":{"expected":"valid result"}}, {"a":{"observations":{"value":1}}}, phases, {}, 1)
    assert report["checks"][0]["status"] == "failed"
    assert not report["complete"]


@pytest.mark.parametrize("recorded,phases", [({},{}),({"a":{"observations":{"value":1}}},{"a":{"call":"passed"}})])
def test_missing_observation_or_phase_is_unrun(recorded,phases):
    report=build_report({"a":{"expected":"valid result"},"b":{"expected":"another result"}},recorded,phases,{},0)
    assert all(check["status"] == "unrun" for check in report["checks"])
    assert not report["complete"]


def test_report_records_expected_observed_and_exit():
    report=build_report({"a":{"expected":2}},{"a":{"observations":{"actual":2}}},
                       {"a":{"setup":"passed","call":"passed","teardown":"passed"}},{"command":"pytest"},0)
    assert report["checks"][0]["expected"] == 2
    assert report["checks"][0]["observations"] == {"actual":2}
    assert report["exit_status"] == 0
    assert report["complete"]


def test_nonfinite_strict_tags():
    body=strict_json({"values":[float("nan"),float("inf"),float("-inf"),None,"",0]})
    decoded=json.loads(body,parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)))
    assert decoded["values"][:3] == [{"kind":"non-finite","value":x} for x in ("NaN","+Infinity","-Infinity")]
    assert decoded["values"][3:] == [None,"",0]


@pytest.mark.parametrize("body",['{', '{"checks":[],"complete":true}', '{"schema_version":1,"checks":NaN}'])
def test_malformed_report_is_incomplete(tmp_path,body):
    path=tmp_path/"broken.json";path.write_text(body)
    with pytest.raises(ValueError):
        read_report(path)


@pytest.mark.parametrize("tamper",["remove-check","failed-phase"])
def test_tampered_complete_report_rejected(tmp_path,tamper):
    report = _reader_report()
    if tamper == "remove-check":
        report["checks"].pop()
    else:
        report["checks"][0]["phases"]["extra"]="failed"
    path=tmp_path/"tampered.json";path.write_text(strict_json(report))
    with pytest.raises(ValueError):
        read_report(path)



def test_registry_requires_uncollected_falsifications(record):
    path=ROOT/"apps/api/core/decision_support/reference_tests/conftest.py"
    spec=importlib.util.spec_from_file_location("reference_config_probe",path)
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    config=SimpleNamespace();module.pytest_configure(config)
    record({"id": "uncollected-registry", "inputs": {"configuration": str(path), "collected_tests": []}},
           {"required_check_ids": list(config._ranking_required)},
           {"required_names": ["test_bad_result_rejected", "test_tampered_complete_report_rejected"]})
    assert any("test_bad_result_rejected" in key for key in config._ranking_required)
    assert any("test_tampered_complete_report_rejected" in key for key in config._ranking_required)



def test_partial_report_is_readable(tmp_path):
    report = _reader_report(partial=True)
    path=tmp_path/"partial.json";path.write_text(strict_json(report))
    loaded=read_report(path)
    assert loaded["complete"] is False
    assert loaded["checks"][1]["status"] == "unrun"
    assert loaded["checks"][1]["observations"] is None


def _load_report_hooks():
    path = ROOT / "apps/api/core/decision_support/reference_tests/conftest.py"
    spec = importlib.util.spec_from_file_location("lifecycle_report_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


@pytest.mark.parametrize("initial", [None, {"observations": {"helper_events": []}},
    {"observations": {"helper_events": [], "pytest": {"phase": "call", "outcome": "passed"}}}],
    ids=["no-record", "empty-events", "phase-only"])
def test_bookkeeping_only_lifecycle_stays_incomplete(initial, record):
    hooks = _load_report_hooks()
    config = SimpleNamespace(_ranking_records={}, _ranking_phases={})
    item = SimpleNamespace(nodeid="probe", config=config)
    if initial is not None:
        item._ranking_record = initial
    for phase in ("setup", "call", "teardown"):
        result = SimpleNamespace(when=phase, outcome="passed", failed=False)
        hook = hooks.pytest_runtest_makereport(item, None)
        next(hook)
        with pytest.raises(StopIteration):
            hook.send(SimpleNamespace(get_result=lambda: result))
    reported = build_report({"probe": {"expected": "actual observation"}},
                            config._ranking_records, config._ranking_phases, {}, 0)
    record({"id": "bookkeeping-probe", "inputs": {"initial": initial, "phases": config._ranking_phases}},
           {"report": reported}, {"status": "unrun", "complete": False})
    assert reported["checks"][0]["status"] == "unrun"
    assert reported["complete"] is False


def test_bookkeeping_only_passing_report_rejected(tmp_path):
    report = build_report({"probe": {"expected": 1, "evidence_level": "arithmetic"}},
                          {"probe": {"observations": {"helper_events": [], "pytest": {"outcome": "passed"}}}},
                          {"probe": {p: "passed" for p in ("setup", "call", "teardown")}}, _report_metadata(), 0)
    report["checks"][0]["status"] = "passed"
    report["complete"] = True
    path = tmp_path / "bookkeeping.json"
    path.write_text(strict_json(report))
    with pytest.raises(ValueError, match="Invalid passing status"):
        read_report(path)


@pytest.mark.parametrize("field", ["generated_at", "git_sha", "source_hashes", "reference_identity", "versions",
                                  "command", "cwd", "evidence_level", "product_browser_acceptance", "check_evidence_level"])
def test_missing_evidence_fields_rejected(tmp_path, field):
    report = _reader_report()
    if field == "check_evidence_level":
        report["checks"][0].pop("evidence_level")
    else:
        report.pop(field)
    path = tmp_path / "missing.json"
    path.write_text(strict_json(report))
    with pytest.raises(ValueError):
        read_report(path)


@pytest.mark.parametrize("field,value", [
    ("generated_at", "not-a-date"), ("generated_at", "2026-10-13T00:00:00"),
    ("generated_at", "2026-10-13T00:00:00+03:30"), ("git_sha", "not-a-sha"),
    ("source_hashes", {}), ("source_hashes", {"synthetic/fixture.py": "wrong"}),
    ("source_hashes", {"../outside.py": "b" * 64}),
    ("reference_identity", {}), ("reference_identity", {"docx_sha256": "bad"}),
    ("versions", []), ("versions", {"python": "3.12.3"}), ("command", "pytest"),
    ("command", []), ("cwd", ""), ("evidence_level", "browser-e2e"),
    ("product_browser_acceptance", True), ("check_evidence_level", None),
    ("check_evidence_level", "browser-e2e"), ("schema_version", True), ("exit_status", False),
], ids=["bad-date", "naive-date", "non-utc-date", "bad-sha", "empty-hashes", "bad-hash", "outside-source",
         "empty-identity", "bad-identity", "bad-versions", "missing-version", "string-command", "empty-command",
         "empty-cwd", "wrong-run-level", "browser-promotion", "null-check-level", "wrong-check-level",
         "boolean-schema", "boolean-exit"])
def test_malformed_evidence_fields_rejected(tmp_path, field, value):
    report = _reader_report()
    if field == "check_evidence_level":
        report["checks"][0]["evidence_level"] = value
    else:
        report[field] = value
    path = tmp_path / "malformed.json"
    path.write_text(strict_json(report))
    with pytest.raises(ValueError):
        read_report(path)


def test_complete_report_with_provenance_is_readable(tmp_path):
    report = _reader_report()
    path = tmp_path / "complete.json"
    path.write_text(strict_json(report))
    loaded = read_report(path)
    assert loaded == report
    assert loaded["complete"] is True
