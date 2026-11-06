# Batch 3 — M11, M12, M22–M25, M27–M29

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

| module_id | operation | actor_kind | project_slot | surface | input_ref | expected | actual | result | na_reason | evidence_ref | defect_id | version_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M11 | risk events | member of A | A/B | direct | risk-events | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M11 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M12 | decision cases | member of A | A/B | direct | decision-cases | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M12 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M22 | correspondence list | member of A | A/B | direct | correspondence | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M22 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M23 | final approval separation | starter and second approver | A | direct | workflow final approve | starter cannot self-approve | suite passed | pass | | `workflow/tests/test_sod_final_approve.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M24 | stakeholder contacts | with and without contact permission | A | direct | stakeholders | sensitive contact redacted | suite passed | pass | | `projects/tests/test_stakeholder_contacts_acl.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M25 | nested report export | with and without wage permission | A | direct | report export | nested sensitive fields redacted | suite passed | pass | | `permissions/tests/test_redaction.py`, `projects/tests/test_nested_export_redaction.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M27 | alert rules and notification inbox | member; anonymous | A | direct | alert-rules; notifications | project list denied across projects; inbox requires sign-in | gap tests passed | pass | | `test_a6_p6_module_gaps.py` M27 and notification test | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M28 | stored-file permission | member vs non-member | A | direct | stored file ACL | permission decision without treating it as live bytes | suite passed; live store did not answer | pass | | `storage/tests/test_stored_file_access.py`. Live fetch is `evidence/file-channel.md` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M29 | access-history trail | authorized reader | A | direct | access changes | before/after trail and secret redaction | 25 passed | pass | | `evidence/p5-handoff.md` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
