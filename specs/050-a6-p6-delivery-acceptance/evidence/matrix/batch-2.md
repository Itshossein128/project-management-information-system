# Batch 2 — M13, M15–M21, M26

version_id: `a46161d3530edfb78c8ebf94b4786d991bea0ba7`

| module_id | operation | actor_kind | project_slot | surface | input_ref | expected | actual | result | na_reason | evidence_ref | defect_id | version_id |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| M13 | overtime list and wage ACL | member of A; wage viewer | A/B | direct | overtime-requests | 200 on A, deny on B; wage hidden without permission | gap test and wage suite passed | pass | | `test_a6_p6_module_gaps.py` M13; `hr/tests/test_wage_acl_and_cost_estimate.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M15 | budgets and commitment separation | member; creator and approver | A | direct | budgets | 200 on A, deny on B; self-approve denied | gap test and commitment suite passed | pass | | `test_a6_p6_module_gaps.py` M15; `cost_control/tests/test_commitment_sod.py` | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M16 | cash-flow list | member of A | A/B | direct | cash-flow | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M16 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M17 | contract list | member of A | A/B | direct | contracts | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M17 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M18 | subcontractor list | member of A | A/B | direct | subcontractors | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M18 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M19 | requisition list | member of A | A/B | direct | requisitions | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M19 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M20 | legacy item catalog | visitor; catalog writer; project manager | org | direct | /api/items/ | visitor read only; project manager cannot write; HR writer can create | visitor 403 on write; manager 403; HR writer 201 | pass | | `inventory/test_visitor_item_writes.py` re-run, 2 passed | D001 | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M21 | material list | member of A | A/B | direct | materials | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M21 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
| M26 | economic snapshot | member of A | A/B | direct | economic/snapshot | 200 on A, deny on B | gap test passed | pass | | `test_a6_p6_module_gaps.py` M26 | | a46161d3530edfb78c8ebf94b4786d991bea0ba7 |
