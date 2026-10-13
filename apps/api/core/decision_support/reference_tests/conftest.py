"""Database-blocked reference suite and optional honest observation report."""

from copy import deepcopy
from datetime import datetime, timezone
import functools
import subprocess
import sys
import pytest
from ranking_reference_fixtures import VALID_CASES, INVALID_CASES, REPRESENTATION_CASES, DOCX_SHA, SOURCE_SHA, BLOCK_SHA, REQUIRED_HARNESS_IDS
import ranking_reference_support as support

PREFIX = "decision_support/reference_tests/test_ranking_reference.py::"


def pytest_addoption(parser):
    parser.addoption("--ranking-reference-report", default=None, help="Write strict reference evidence JSON")


def pytest_configure(config):
    config._ranking_required = {}
    for function, cases in [("test_valid_parity",VALID_CASES),("test_invalid_rejection",INVALID_CASES),("test_representation",REPRESENTATION_CASES)]:
        for case in cases:
            config._ranking_required[PREFIX + function + "[" + case["id"] + "]"] = {"case":deepcopy(case),"expected":deepcopy(case),"evidence_level":"arithmetic"}
    for name in ["test_source_fidelity","test_published_reference_interface","test_fixture_invariants"]:
        config._ranking_required[PREFIX+name] = {"expected":{"assertions":name},"evidence_level":"arithmetic"}
    for key in REQUIRED_HARNESS_IDS:
        config._ranking_required.setdefault(key, {"expected": {"assertions": key}, "evidence_level": "arithmetic"})
    config._ranking_records = {}
    config._ranking_phases = {}


@pytest.hookimpl(tryfirst=True)
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "decision_support/reference_tests/" in item.nodeid:
            params=deepcopy(getattr(getattr(item,"callspec",None),"params",{}))
            config._ranking_required.setdefault(item.nodeid,{"expected":{"assertions":item.name,"inputs":params},"evidence_level":"arithmetic"})


@pytest.fixture(autouse=True)
def block_reference_database(django_db_blocker):
    with django_db_blocker.block():
        yield


@pytest.fixture(autouse=True)
def record_helper_observations(request, monkeypatch):
    request.node._ranking_record = {"observations":{"helper_events":[]}}
    events=request.node._ranking_record["observations"]["helper_events"]
    for name in ("authenticate","validate_shape","reference","observe","compare","check_rejection","build_report","strict_json","read_report"):
        original=getattr(support,name)
        def wrap(original, name):
            @functools.wraps(original)
            def wrapped(*args,**kwargs):
                event={"helper":name,"inputs":support.json_safe(args),"kwargs":support.json_safe(kwargs)}
                events.append(event)
                try:
                    value=original(*args,**kwargs)
                    event["value"]=support.json_safe(value)
                    return value
                except Exception as error:
                    event.update(error_class=type(error).__name__,error_message=str(error))
                    raise
            return wrapped
        wrapped=wrap(original,name)
        monkeypatch.setattr(support,name,wrapped)
        if hasattr(request.module,name):
            monkeypatch.setattr(request.module,name,wrapped)
    yield


@pytest.fixture
def record(request):
    def capture(case, observations, expected=None):
        request.node._ranking_record.update(case=deepcopy(case),expected=deepcopy(expected),observations=deepcopy(observations))
    return capture


@pytest.hookimpl(hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome=yield
    report=outcome.get_result()
    item.config._ranking_phases.setdefault(item.nodeid,{})[report.when]=report.outcome
    observed=deepcopy(getattr(item,"_ranking_record",{}))
    observed["pytest"]={"phase":report.when,"outcome":report.outcome,
        "failure":str(report.longrepr) if report.failed else None}
    item.config._ranking_records[item.nodeid]=observed


def pytest_sessionfinish(session, exitstatus):
    destination=session.config.getoption("--ranking-reference-report")
    if not destination:
        return
    import django
    import rest_framework
    paths=[]
    for relative in ["apps/api/core/decision_support","apps/web/src/components/decision-support","apps/web/e2e/tests/helpers"]:
        paths.extend(p for p in (support.ROOT/relative).rglob("*") if p.suffix in (".py",".ts",".tsx"))
    for relative in ["apps/api/core/conftest.py","apps/api/core/pytest.ini","apps/api/core/config/settings.py",
                     "apps/web/src/app/routes/project-decision-support.tsx","apps/web/src/app/lib/api/decision-support.ts",
                     "apps/web/src/app/locales/en.json","apps/web/src/app/locales/fa.json",
                     "apps/web/e2e/tests/decision-execution-records.spec.ts","apps/web/e2e/playwright.config.ts",
                     "docs/decision-support/09-ranking-reference.md","docs/document (10).docx"]:
        path=support.ROOT/relative
        if path.is_file(): paths.append(path)
    metadata={"generated_at":datetime.now(timezone.utc).isoformat(),
        "git_sha":subprocess.check_output(["git","rev-parse","HEAD"],cwd=support.ROOT,text=True).strip(),
        "source_hashes":{str(p.relative_to(support.ROOT)):support.digest(p.read_bytes()) for p in sorted(set(paths))},
        "reference_identity":{"docx_sha256":DOCX_SHA,"source_sha256":SOURCE_SHA,"block_sha256":BLOCK_SHA},
        "versions":{"python":sys.version.split()[0],"django":django.get_version(),"drf":rest_framework.VERSION,"pytest":pytest.__version__},
        "command":[sys.executable,"-m","pytest",*session.config.invocation_params.args],
        "cwd":"apps/api/core","evidence_level":"arithmetic", "product_browser_acceptance":False}
    report=support.build_report(session.config._ranking_required,session.config._ranking_records,session.config._ranking_phases,metadata,exitstatus)
    path=support.Path(destination)
    path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(support.strict_json(report)+"\n")
