"""Recount authored schedule fixtures without calling the product importer."""

import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from schedule.services.mpp_convert import convert_mpp_to_mspdi

EVIDENCE = Path(__file__).resolve().parent
REPO = EVIDENCE.parents[2]
FIXTURES = EVIDENCE / "fixtures"


def _local(tag: str) -> str:
    return tag.split("}")[-1]


def _xml_counts(path: Path) -> dict:
    root = ET.parse(path).getroot()
    tasks = [el for el in root.iter() if _local(el.tag) == "Task"]
    summaries = 0
    milestones = 0
    links = []
    for task in tasks:
        for child in list(task):
            name = _local(child.tag)
            if name == "Summary" and (child.text or "").strip() == "1":
                summaries += 1
            elif name == "Milestone" and (child.text or "").strip() == "1":
                milestones += 1
            elif name == "PredecessorLink":
                uid = ""
                for link_child in list(child):
                    if _local(link_child.tag) == "PredecessorUID":
                        uid = (link_child.text or "").strip()
                links.append(uid)
    return {
        "root": _local(root.tag),
        "tasks": len(tasks),
        "summaries": summaries,
        "milestones": milestones,
        "predecessor_links": len(links),
        "predecessor_uids": links,
    }


def _xer_tables(path: Path) -> dict:
    tables: dict[str, list[list[str]]] = {}
    fields: list[str] = []
    current = ""
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.startswith("%T\t"):
            current = line.split("\t", 1)[1]
            tables.setdefault(current, [])
            fields = []
        elif line.startswith("%F\t"):
            fields = line.split("\t")[1:]
        elif line.startswith("%R\t") and current:
            values = line.split("\t")[1:]
            tables[current].append(values if not fields else list(zip(fields, values, strict=False)))
    return tables


SUMMARY_PREDECESSORS = {
    "8055": "تکمیل تاسیسات و نازک کاری بلوک 31-30",
    "8084": "تکمیل تاسیسات و نازک کاری بلوک 39-38",
    "8102": "تکمیل تاسیسات و نازک کاری بلوک 29-28",
    "8120": "تکمیل تاسیسات و نازک کاری بلوک 37-36",
}


def test_historical_predecessor_uids_are_present_summaries():
    """Read MSPDI Summary flags. Do not call the importer or its leaf UID map."""
    path = REPO / "real-data" / "plan.mpp"
    original = path.read_bytes()
    xml = convert_mpp_to_mspdi(original)
    assert path.read_bytes() == original

    found: dict[str, tuple[str, str]] = {}
    for el in ET.fromstring(xml).iter():
        if _local(el.tag) != "Task":
            continue
        uid = name = summary = ""
        for child in list(el):
            child_name = _local(child.tag)
            text = (child.text or "").strip()
            if child_name == "UID":
                uid = text
            elif child_name == "Name":
                name = text
            elif child_name == "Summary":
                summary = text
        if uid in SUMMARY_PREDECESSORS:
            found[uid] = (name, summary)
    assert set(found) == set(SUMMARY_PREDECESSORS)
    for uid, expected_name in SUMMARY_PREDECESSORS.items():
        assert found[uid] == (expected_name, "1")
    contract = json.loads((EVIDENCE / "control-figures.json").read_text(encoding="utf-8"))
    classified = {
        row["id"]: row
        for row in contract["historical_probe_not_a_target"]
        if row["id"].startswith("H-PRED-")
    }
    for uid in SUMMARY_PREDECESSORS:
        row = classified[f"H-PRED-{uid}"]
        assert row["classification"] == "present_summary"
        assert "leaves" in row["cause"]


def test_historical_duration_ids_match_schedule_contract():
    contract = json.loads((EVIDENCE / "control-figures.json").read_text(encoding="utf-8"))
    ids = [row["id"] for row in contract["historical_probe_not_a_target"]]
    assert "H-DUR-شروع" in ids
    assert "H-DUR-پایان" in ids
    assert "H-DUR-start" not in ids
    assert "H-DUR-finish" not in ids


def test_employer_file_fingerprint_matches_contract():
    contract = json.loads((EVIDENCE / "control-figures.json").read_text(encoding="utf-8"))
    recorded = contract["employer_file"]
    payload = (REPO / recorded["path"]).read_bytes()
    assert hashlib.sha256(payload).hexdigest() == recorded["sha256"]
    assert len(payload) == recorded["size_bytes"]
    assert payload.startswith(b"\xd0\xcf\x11\xe0\xa1\xb1\x1a\xe1")


def test_authored_xml_counts_match_contract():
    contract = json.loads((EVIDENCE / "control-figures.json").read_text(encoding="utf-8"))
    for name, expected in contract["xml"].items():
        actual = _xml_counts(FIXTURES / name)
        if "root" in expected:
            assert actual["root"] == expected["root"]
            continue
        assert actual["tasks"] == expected["tasks"]
        assert actual["summaries"] == expected["summaries"]
        assert actual["milestones"] == expected["milestones"]
        assert actual["predecessor_links"] == expected["predecessor_links"]
        if "predecessor_uids" in expected:
            assert actual["predecessor_uids"] == expected["predecessor_uids"]
        if "zero_duration" in expected:
            assert expected["zero_duration"] in (FIXTURES / name).read_text(encoding="utf-8")


def test_authored_xer_counts_match_contract():
    contract = json.loads((EVIDENCE / "control-figures.json").read_text(encoding="utf-8"))
    for name, expected in contract["xer"].items():
        text = (FIXTURES / name).read_text(encoding="utf-8")
        if "starts_with_ermhdr" in expected:
            assert text.startswith("ERMHDR") is expected["starts_with_ermhdr"]
            continue
        tables = _xer_tables(FIXTURES / name)
        for table, count in expected.items():
            if table in {"zero_duration_hours", "pred_task_ids"}:
                continue
            assert len(tables.get(table, [])) == count
        if "pred_task_ids" in expected:
            preds = tables["TASKPRED"]
            ids = [dict(row).get("pred_task_id") for row in preds]
            assert ids == expected["pred_task_ids"]
        if "zero_duration_hours" in expected:
            task_row = dict(tables["TASK"][0])
            assert task_row["target_drtn_hr_cnt"] == expected["zero_duration_hours"]
