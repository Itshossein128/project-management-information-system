# Defects

| defect_id | requirement_ids | scenario_ids | blocking | in_scope | status | before_evidence | after_evidence | criteria_unchanged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D001 | A6-R32, A6-R38 | U10, M20 | true | true | fixed | `inventory/test_visitor_item_writes.py::test_non_visitor_can_still_create_item` expected 201 from a project manager and received 403 on `/api/items/` | The same file now expects the project manager to receive 403 and an HR catalog writer to receive 201. Re-run: 2 passed. | true |

`criteria_unchanged` stays true. The visitor still may read and may not write. The positive create belongs to the organization catalog writer, which is the rule already implemented by `IsOrgCatalogWriteAuthority`. The old test treated every signed-in non-visitor as that writer.

Out of scope, `in_scope` false, no product change:

| defect_id | requirement_ids | scenario_ids | blocking | in_scope | status | before_evidence | after_evidence | criteria_unchanged |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| D002 | A6-R54 | none | false | false | deferred_external | Role templates for project types are outside this commitment | none | true |

| D003 | A6-R01, A6-R04, A6-R08 | U01, U09, U19 | true | true | fixed | `test_only_account_administrators_can_create_people` and the two account-status tests received 403 for the `hr` group | `IsOrganizationalAccountAdmin` allows `admin` and `hr` and still refuses staff alone. Re-run: 10 passed. | true |

The access-history screen also could not start because both routes used the file path as the same route id. `apps/web/src/app/routes/business-setup.routes.ts` now sets `project-access-history` and `settings-access-history`. That is D004.

| D004 | A6-R48, A6-R53 | U18, US3 | true | true | fixed | Vite: `Unable to define routes with duplicate route id: "routes/access-history"` | Route ids are distinct. Vite reached `Local:`. | true |

| D005 | A6-R46 | M14 | false | true | open | `test_superuser_break_glass_can_approve_as_preparer_and_submitter` expected 200 and received 403. The test does not give the superuser membership or an explicit reason. | Not changed. Automatic superuser approval would contradict the explicit-reason rule, so this row stays open rather than being turned into a pass. | true |

No other in-scope blocking failure from the catalog or account-administration fixes remained. D005 stays open and is not counted as a pass. The live file store and the live sender are external blocks, not product defects.
