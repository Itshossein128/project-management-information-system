"""Independent ordered fixtures for the preserved ranking sample; test-only."""

from math import sqrt
from copy import deepcopy

FIELDS = ('criteria', 'alternatives', 'weights', 'types', 'matrix')
CLASSIFICATIONS = ('valid', 'invalid', 'representation')

DOCX_PATH = "docs/document (10).docx"
MARKDOWN_PATH = "docs/decision-support/09-ranking-reference.md"
DOCX_SHA = "52946a0ff62205bebf007eda3a6c860d5f010311194c3740316d6a2a2369e282"
SOURCE_SHA = "ae0f35b52bb9231d06cc416d1972f248257ec34dbf07fcd8658948ac55b83e26"
BLOCK_SHA = "8304307300aba81d18c8669d1e5d2d3ce3578df03498359528ad8ab2e25328db"
PUBLISHED = {
    "id": "published", "classification": "valid", "families": ["mixed", "published"],
    "requirements": ["FR-001", "FR-002", "FR-003"], "story": "US1", "success": ["SC-001", "SC-002"],
    "inputs": [["تجربه", "قیمت"], ["پیمانکار الف", "پیمانکار ب"], [1, 1],
               ["benefit", "cost"], [[10, 100], [5, 200]]],
    "scores": {"SAW": [1.0, .5], "TOPSIS": [1.0, 0.0]},
    "order": {"SAW": ["پیمانکار الف", "پیمانکار ب"], "TOPSIS": ["پیمانکار الف", "پیمانکار ب"]},
}



def valid_case(identifier, criteria, alternatives, weights, types, matrix, saw, topsis, orders=None, families=()):
    return {"id": identifier, "classification": "valid", "families": list(families),
            "requirements": ["FR-004", "FR-005", "FR-006", "FR-007"], "story": "US2", "success": ["SC-002"],
            "inputs": [criteria, alternatives, weights, types, matrix],
            "scores": {"SAW": saw, "TOPSIS": topsis},
            "order": orders or {"SAW": alternatives, "TOPSIS": alternatives}}


VALID_CASES = [
    PUBLISHED,
    valid_case("one-by-one", ["Quality"], ["Only"], [2], ["benefit"], [[10]], [1], [.5], families=["1x1"]),
    valid_case("rectangular-zero-weight", ["Quality", "Cost", "Unused"], ["A", "B"], [2,3,0],
               ["benefit","cost","benefit"], [[10,100,5],[5,200,10]], [1,.5], [1,0], families=["2x3","mixed","zero-weight"]),
    valid_case("maximum", [f"C{i}" for i in range(1,11)], [f"A{i}" for i in range(1,11)],
               list(range(1,11)), ["benefit"]*10, [[i]*10 for i in range(1,11)],
               [i/10 for i in range(1,11)], [(i-1)/9 for i in range(1,11)],
               {"SAW": [f"A{i}" for i in range(10,0,-1)], "TOPSIS": [f"A{i}" for i in range(10,0,-1)]}, ["10x10","benefit-only"]),
    valid_case("cost-only", ["Cost"], ["A","B"], [1], ["cost"], [[10],[20]], [1,.5], [1,0], families=["cost-only"]),
    valid_case("benefit-zero", ["Quality"], ["A","B"], [1], ["benefit"], [[0],[10]], [0,1], [0,1],
               {"SAW":["B","A"],"TOPSIS":["B","A"]}, ["benefit-only","valid-zero"]),
    valid_case("exact-ties", ["Quality"], ["Alpha","گزینه ب"], [1], ["benefit"], [[10],[10]], [1,1], [.5,.5], families=["ties","bilingual"]),
    valid_case("permuted-ties", ["Quality"], ["گزینه ب","Alpha"], [1], ["benefit"], [[10],[10]], [1,1], [.5,.5], families=["ties","permutation"]),
    valid_case("constant-mixed", ["Quality","Cost"], ["A","B"], [2,1], ["benefit","cost"], [[1,3],[1,3]], [1,1], [.5,.5], families=["constant-columns"]),
    valid_case("weights-relative", ["Quality","Cost"], ["A","B"], [2,3], ["benefit","cost"], [[10,100],[5,200]], [1,.5], [1,0], families=["scaled-weights"]),
    valid_case("weights-scaled", ["Quality","Cost"], ["A","B"], [20,30], ["benefit","cost"], [[10,100],[5,200]], [1,.5], [1,0], families=["scaled-weights"]),
    valid_case("disagreement", ["Quality","Experience"], ["A","B"], [21,10], ["benefit","benefit"], [[10,1],[6,5]],
               [23/31,113/155], [21*sqrt(26)/(21*sqrt(26)+10*sqrt(136)),10*sqrt(136)/(21*sqrt(26)+10*sqrt(136))],
               {"SAW":["A","B"],"TOPSIS":["B","A"]}, ["disagreement","unequal-weights"]),
]
for case in VALID_CASES:
    case["weights_normalized"] = [float(w)/sum(case["inputs"][2]) for w in case["inputs"][2]]
VALID_CASES[7]["companion"] = "exact-ties"
VALID_CASES[10]["companion"] = "weights-relative"


def invalid_case(identifier, inputs, path, code):
    return {"id": identifier, "classification": "invalid", "families": [identifier],
            "requirements": ["FR-008"], "story": "US3", "success": ["SC-003"],
            "inputs": inputs, "issue": {"path": path, "code": code},
            "reference_errors": ["ValueError", "TypeError"]}


INVALID_CASES = []
for index, field in [(0,"criteria"),(1,"alternatives")]:
    for label, names, path, code in [
        ("empty", [], field, "dimension_invalid"),
        ("too-many", [f"Name{i}" for i in range(11)], field, "dimension_invalid"),
        ("blank", ["", "B"], field+".0", "name_empty"),
        ("duplicate", ["A", "A"], field+".1", "name_duplicate"),
    ]:
        inputs = deepcopy(PUBLISHED["inputs"]); inputs[index] = names
        INVALID_CASES.append(invalid_case(field+"-"+label, inputs,path,code))
for index, field in [(2,"weights"),(3,"types")]:
    for label in ["short","long"]:
        inputs=deepcopy(PUBLISHED["inputs"])
        inputs[index]=inputs[index][:-1] if label == "short" else inputs[index]+[inputs[index][0]]
        INVALID_CASES.append(invalid_case(field+"-"+label,inputs,field,"length_mismatch"))
for label in ["short","long"]:
    inputs=deepcopy(PUBLISHED["inputs"])
    inputs[4]=inputs[4][:-1] if label == "short" else inputs[4]+[inputs[4][0]]
    INVALID_CASES.append(invalid_case("rows-"+label,inputs,"performance_matrix","matrix_shape"))
    inputs=deepcopy(PUBLISHED["inputs"])
    inputs[4][0]=inputs[4][0][:-1] if label == "short" else inputs[4][0]+[1]
    INVALID_CASES.append(invalid_case("columns-"+label,inputs,"performance_matrix.0","length_mismatch"))
for field, index in [("weight",2),("cell",4)]:
    for label,value in [("empty",""),("null",None),("text","not numeric"),("negative",-1),
                        ("nan",float("nan")),("infinity",float("inf")),("negative-infinity",float("-inf"))]:
        inputs=deepcopy(PUBLISHED["inputs"])
        if field == "weight":
            inputs[2][0]=value;path="weights.0"
            code="weight_negative" if label == "negative" else "non_finite" if "infinity" in label or label=="nan" else "non_numeric"
        else:
            inputs[4][0][0]=value;path="performance_matrix.0.0"
            code="negative_value" if label == "negative" else "non_finite" if "infinity" in label or label=="nan" else "empty_cell" if label in ("empty","null") else "non_numeric"
        INVALID_CASES.append(invalid_case(field+"-"+label,inputs,path,code))
for identifier, field, value, path, code in [
    ("invalid-type",3,["wrong","cost"],"types.0","invalid_type"),
    ("weights-zero",2,[0,0],"weights","weights_all_zero"),
    ("cost-zero",4,[[10,0],[5,200]],"performance_matrix.0.1","cost_zero"),
    ("benefit-all-zero",4,[[0,100],[0,200]],"criteria.0","benefit_column_all_zero"),
]:
    inputs=deepcopy(PUBLISHED["inputs"]);inputs[field]=value
    INVALID_CASES.append(invalid_case(identifier,inputs,path,code))
inputs=deepcopy(PUBLISHED["inputs"]);inputs[2]=[0,1];inputs[4]=[[0,100],[0,200]]
INVALID_CASES.append(invalid_case("zero-weight-zero-column",inputs,"criteria.0","benefit_column_all_zero"))


def representation_case(identifier, inputs, reference_accepts, product_accepts, issue=None):
    return {"id":identifier,"classification":"representation","families":[identifier],
            "requirements":["FR-009"],"story":"US3","success":["SC-003"],"inputs":inputs,
            "reference_accepts":reference_accepts,"product_accepts":product_accepts,"issue":issue}


REPRESENTATION_CASES = [
    representation_case("numeric-text",[["Q"],["A"],["1"],["benefit"],[["2"]]],True,True),
    representation_case("boolean-cell",[["Q"],["A"],[1],["benefit"],[[True]]],True,False,{"code":"non_numeric","path":"performance_matrix.0.0"}),
    representation_case("boolean-weight",[["Q"],["A"],[True],["benefit"],[[2]]],True,True),
    representation_case("trimmed-duplicate-criteria",[["Q"," Q "],["A"],[1,1],["benefit","benefit"],[[2,2]]],True,False,{"code":"name_duplicate","path":"criteria.1"}),
    representation_case("trimmed-duplicate-alternatives",[["Q"],["A"," A "],[1],["benefit"],[[2],[3]]],True,False,{"code":"name_duplicate","path":"alternatives.1"}),
    representation_case("none-name",[[None],["A"],[1],["benefit"],[[2]]],True,False,{"code":"name_empty","path":"criteria.0"}),
    representation_case("trimmed-type",[["Q"],["A"],[1],[" benefit "],[[2]]],False,True),
]

# Reviewed registry: explicit file selection must not omit required falsification checks.
REQUIRED_HARNESS_IDS = ('decision_support/reference_tests/test_ranking_reference_harness.py::test_observation_copies_inputs',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_observation_retains_error',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_reference_database_is_blocked',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[message]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[comment]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[whitespace]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[missing]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[duplicate]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_counterfeit_reference_rejected[source]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_shape_rejected[import '
 'os\\ndef rank_options(a,b,c,d,e): pass]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_shape_rejected[from '
 'math import isfinite, sqrt\\ndef rank_options(a): pass]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_shape_rejected[from '
 'math import isfinite, sqrt\\ndef wrong(a,b,c,d,e): pass]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_shape_rejected[from '
 'math import isfinite, sqrt\\n@decorator\\ndef rank_options(criteria, alternatives, weights, '
 'types, matrix): pass]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_shape_rejected[from '
 'math import isfinite, sqrt\\ndef rank_options(criteria, alternatives, weights, types, matrix): '
 "pass\\nprint('extra')]",
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows0]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows1]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows2]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows3]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows4]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows5]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows6]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows7]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows8]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[None]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bad_result_rejected[rows10]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_tie_order_is_exact',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_absolute_tolerance_boundary',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_rejection_fails[observation0-reference-None]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_rejection_fails[observation1-reference-None]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_rejection_fails[observation2-product-issue2]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_rejection_fails[observation3-product-issue3]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_wrong_rejection_fails[observation4-product-issue4]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_failed_phase_cannot_pass[setup]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_failed_phase_cannot_pass[call]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_failed_phase_cannot_pass[teardown]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_observation_or_phase_is_unrun[recorded0-phases0]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_observation_or_phase_is_unrun[recorded1-phases1]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_report_records_expected_observed_and_exit',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_nonfinite_strict_tags',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_report_is_incomplete[{]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_report_is_incomplete[{"checks":[],"complete":true}]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_report_is_incomplete[{"schema_version":1,"checks":NaN}]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_tampered_complete_report_rejected[remove-check]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_tampered_complete_report_rejected[failed-phase]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_registry_requires_uncollected_falsifications',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_partial_report_is_readable',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bookkeeping_only_lifecycle_stays_incomplete[no-record]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bookkeeping_only_lifecycle_stays_incomplete[empty-events]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bookkeeping_only_lifecycle_stays_incomplete[phase-only]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_bookkeeping_only_passing_report_rejected')

# Provenance falsifications remain required under partial file selection.
REQUIRED_HARNESS_IDS += ('decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[generated_at]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[git_sha]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[source_hashes]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[reference_identity]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[versions]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[command]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[cwd]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[evidence_level]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[product_browser_acceptance]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_missing_evidence_fields_rejected[check_evidence_level]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[bad-date]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[naive-date]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[non-utc-date]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[bad-sha]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[empty-hashes]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[bad-hash]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[outside-source]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[empty-identity]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[bad-identity]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[bad-versions]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[missing-version]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[string-command]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[empty-command]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[empty-cwd]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[wrong-run-level]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[browser-promotion]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[null-check-level]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[wrong-check-level]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[boolean-schema]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_malformed_evidence_fields_rejected[boolean-exit]',
 'decision_support/reference_tests/test_ranking_reference_harness.py::test_complete_report_with_provenance_is_readable')
