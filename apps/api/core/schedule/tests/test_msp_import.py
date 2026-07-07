"""MSP XML import parser tests (no database required)."""

from schedule.services.msp_import import build_preview, parse_msp_xml

SAMPLE_MSP_XML = b"""<?xml version="1.0" encoding="UTF-8"?>
<Project xmlns="http://schemas.microsoft.com/project">
  <Tasks>
    <Task>
      <UID>1</UID>
      <ID>1</ID>
      <Name>Phase 1</Name>
      <OutlineLevel>1</OutlineLevel>
      <OutlineNumber>1</OutlineNumber>
      <WBS>1</WBS>
      <Summary>1</Summary>
    </Task>
    <Task>
      <UID>2</UID>
      <ID>2</ID>
      <Name>Sub phase</Name>
      <OutlineLevel>2</OutlineLevel>
      <OutlineNumber>1.1</OutlineNumber>
      <WBS>1.1</WBS>
      <Summary>1</Summary>
    </Task>
    <Task>
      <UID>3</UID>
      <ID>3</ID>
      <Name>Activity A</Name>
      <OutlineLevel>3</OutlineLevel>
      <OutlineNumber>1.1.1</OutlineNumber>
      <WBS>1.1.1</WBS>
      <Summary>0</Summary>
      <Duration>PT40H0M0S</Duration>
      <PercentComplete>25</PercentComplete>
      <Start>2026-01-01T08:00:00</Start>
      <Finish>2026-01-06T17:00:00</Finish>
      <PredecessorLink>
        <PredecessorUID>2</PredecessorUID>
        <Type>1</Type>
      </PredecessorLink>
    </Task>
  </Tasks>
</Project>
"""


def test_parse_msp_xml_extracts_tasks():
    result = parse_msp_xml(SAMPLE_MSP_XML)
    assert len(result.tasks) == 3
    activity = next(t for t in result.tasks if t.uid == '3')
    assert activity.duration_days == 5
    assert activity.percent_complete is not None


def test_parse_msp_xml_rejects_invalid_root():
    try:
        parse_msp_xml(b'<NotProject></NotProject>')
        assert False, 'expected ValueError'
    except ValueError as exc:
        assert 'Project' in str(exc)


def test_build_preview_returns_tree():
    parsed = parse_msp_xml(SAMPLE_MSP_XML)
    preview = build_preview(parsed)
    assert len(preview['wbs_tree']) >= 1
    assert len(preview['activities']) == 1
    assert isinstance(preview['warnings'], list)
