"""033 RED-phase scaffolding (feature 033-daily-sections-grid).

Tasks: T034, T050
Scope: Receipts-only main table, consumption details and document-anchored reconciliation.

This module is intentionally empty during the RED phase so that the suite can
be invoked from day one. Tests arrive with the tasks above; until then the
module is skipped at collection with reason below.
"""

import pytest

pytest.skip(
    "Feature 033 RED scaffolding: tests land with T034, T050",
    allow_module_level=True,
)
