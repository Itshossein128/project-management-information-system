# B04 Research

## Daily summary matching

- **Decision** Use one correlated existence predicate for all supplied activity dimensions against eligible activities of the selected report version. Use the existing one-source projected activity where the rollup and provenance establish equivalence. Verify lineage for both unit and department activity kinds, including revised summaries.
- **Rationale** `daily_report_aggregation.py` copies discipline, contractor and block into each projected activity and records source identity via `DailyReportDerivedSource`. A single existence predicate also returns the parent once when multiple rows qualify. Apply the new predicate to the daily list action. Keep its existing current-only default and preserve explicit historical retrieval behavior outside the official log.
- **Alternatives considered** Separate existence checks admit split-row false positives. Joining child rows into the parent list requires deduplication and can distort pagination. Looking up current unit reports independently of the summary can change the meaning of version-bound evidence.

## Activity selection and aggregation

- **Decision** Extend `activity_log_queryset` for normalized filters and retain its B02 predicates. Use the same filtered base for pagination, grouped database aggregation and FILE1. Compute full row count and headcount plus measured quantity by unit. Use stored contractor identity for exact filtering.
- **Rationale** Activity list and FILE1 already consume that queryset. Current list responses cache page metadata and page rows, while the UI sums the page. FILE1 already checks the measured flag. Keep decimal precision for aggregation and preserve the workbook's numeric zero and unknown presentation.
- **Alternatives considered** Client-side summing fails by construction on multiple pages. Export-only recalculation leaves the UI inconsistent. Name-only contractor selection can merge separate identities.

## URL, cache and compatibility

- **Decision** Share typed activity filter serialization, keep existing comma-separated parameters and names as compatible inputs, and use explicit URL values for date presets. Keep page state in history and include a normalized filter fingerprint and project/version scope in cache keys. Reuse approval invalidation and check client freshness within SC-004.
- **Rationale** Current activity UI uses date defaults and replacement navigation and the API has separate list and export clients. Shared serialization prevents drift. Permission and dimension validation must run before a cached response. A superseded report remains accessible through authorized history.
- **Alternatives considered** Local component state cannot reproduce shared links. A distinct export filter implementation can diverge from the activity list. The separately labeled B03 date-range workbook continues to use its own dates and permission contract.

## Evidence boundaries

- **Decision** Treat the dated QA reports as regression inputs. Use repository source and the accepted B01/B04 clarification for design. Run fresh API, browser, workbook and timing checks after implementation.
- **Rationale** The knowledge index is stale and the prior refresh could not connect. Historical QA scopes differ. Source inspection confirms entry points and proposed reuse.
- **Alternatives considered** Reusing historical QA as acceptance proof would leave current release behavior unverified.
