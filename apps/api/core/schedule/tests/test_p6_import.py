"""P6 XER import tests."""

import pytest

from schedule.services.p6_import import parse_p6_xer


SAMPLE_XER = b"""ERMHDR\t18.8\t2024-01-01\tProject
%T\tPROJWBS
%F\twbs_id\tparent_wbs_id\twbs_short_name\twbs_name\tseq_num
%R\t1\t\t1\tProject Root\t1
%R\t2\t1\t1.1\tPhase 1\t2
%T\tTASK
%F\ttask_id\twbs_id\ttask_code\ttask_name\ttarget_drtn_hr_cnt
%R\t100\t2\tA100\tExcavation\t40
%T\tTASKPRED
%F\ttask_id\tpred_task_id\tpred_type\tlag_hr_cnt
"""


@pytest.mark.django_db
class TestP6ImportParser:
    def test_parse_minimal_xer(self):
        result = parse_p6_xer(SAMPLE_XER)
        assert len(result.tasks) >= 2
        assert any(t.is_summary for t in result.tasks)
        assert any(not t.is_summary for t in result.tasks)

    def test_invalid_xer_raises(self):
        with pytest.raises(ValueError):
            parse_p6_xer(b'not an xer file')
