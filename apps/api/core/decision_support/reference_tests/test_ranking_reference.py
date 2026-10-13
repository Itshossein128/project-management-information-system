
import hashlib
from ranking_reference_fixtures import DOCX_PATH, MARKDOWN_PATH, SOURCE_SHA, FIELDS
from ranking_reference_support import ROOT, authenticate, validate_shape
from ranking_reference_fixtures import PUBLISHED
from ranking_reference_support import reference, observe
import math
import pytest
from ranking_reference_fixtures import VALID_CASES
from ranking_reference_support import compare
from decision_support.services.saw_service import compute_saw
from decision_support.services.topsis_service import compute_topsis
from ranking_reference_fixtures import INVALID_CASES, REPRESENTATION_CASES
from ranking_reference_support import check_rejection

def test_source_fidelity():
    source = authenticate((ROOT / MARKDOWN_PATH).read_text(), (ROOT / DOCX_PATH).read_bytes())
    assert hashlib.sha256(source.encode()).hexdigest() == SOURCE_SHA
    assert len(source.splitlines()) == 91
    assert len(source) == 3722
    validate_shape(source)



def test_published_reference_interface():
    function = reference()
    assert callable(function), "Authenticated reference must be evaluable"
    observation = observe(function, PUBLISHED["inputs"])
    assert observation["error_class"] is None
    assert observation["input_unchanged"]
    result = observation["value"]
    assert set(result) == {"SAW", "TOPSIS"}
    names = PUBLISHED["inputs"][1]
    for method, rows in result.items():
        assert [r["option"] for r in rows] == PUBLISHED["order"][method]
        for row in rows:
            assert set(row) == {"option", "SAW", "TOPSIS"}
            for score in ("SAW", "TOPSIS"):
                assert row[score] == PUBLISHED["scores"][score][names.index(row["option"])]


ENGINES = {"SAW": compute_saw, "TOPSIS": compute_topsis}


@pytest.mark.parametrize("case", VALID_CASES, ids=lambda case: case["id"])
def test_valid_parity(case, record):
    reference_observation = observe(reference(), case["inputs"])
    products = {method: observe(engine, case["inputs"]) for method, engine in ENGINES.items()}
    record(case, {"reference": reference_observation, **products}, case["scores"])
    names = case["inputs"][1]
    assert reference_observation["error_class"] is None
    assert reference_observation["input_unchanged"]
    result = reference_observation["value"]
    assert set(result) == {"SAW", "TOPSIS"}
    for method, observed in products.items():
        assert observed["error_class"] is None
        assert observed["input_unchanged"]
        reference_rows = result[method]
        for other in ("SAW", "TOPSIS"):
            compare(reference_rows, other, names, case["scores"][other], case["order"][method])
        assert all(set(row) == {"option", "SAW", "TOPSIS"} for row in reference_rows)
        value = observed["value"]
        compare(value["ranking"], "score", names, case["scores"][method], case["order"][method])
        compare(value["ranking"], "score", names,
                [next(row[method] for row in reference_rows if row["option"] == name) for name in names],
                case["order"][method])
        assert value["weights_normalized"] == pytest.approx(case["weights_normalized"], abs=1e-9, rel=0)
        assert [row["rank"] for row in value["ranking"]] == list(range(1,len(names)+1))
        if method == "TOPSIS":
            for row in value["ranking"]:
                assert row["score"] == row["closeness"]
                assert math.isfinite(row["d_best"]) and row["d_best"] >= 0
                assert math.isfinite(row["d_worst"]) and row["d_worst"] >= 0


def test_fixture_invariants(record):
    by_id = {case["id"]: case for case in VALID_CASES}
    record({"id": "fixture-invariants", "inputs": VALID_CASES},
           {"values": {case["id"]: case["inputs"][2] + [x for row in case["inputs"][4] for x in row]
                       for case in VALID_CASES},
            "companions": {key: {"scores": by_id[key]["scores"], "order": by_id[key]["order"]}
                           for key in ("weights-scaled", "weights-relative", "disagreement")}},
           {"bounds": [0, 1000], "minimum_nonzero": .1, "classification": "valid",
            "scaled_weights": "equal scores and orders", "disagreement": "different method orders"})
    for case in VALID_CASES:
        assert case["classification"] == "valid"
        for value in case["inputs"][2] + [x for row in case["inputs"][4] for x in row]:
            assert 0 <= value <= 1000
            assert value == 0 or value >= .1
    assert by_id["weights-scaled"]["scores"] == by_id["weights-relative"]["scores"]
    assert by_id["weights-scaled"]["order"] == by_id["weights-relative"]["order"]
    assert by_id["disagreement"]["order"]["SAW"] != by_id["disagreement"]["order"]["TOPSIS"]



@pytest.mark.parametrize("case", INVALID_CASES, ids=lambda case: case["id"])
def test_invalid_rejection(case, record):
    observations = {"reference": observe(reference(),case["inputs"])}
    observations.update({method:observe(engine,case["inputs"]) for method,engine in ENGINES.items()})
    record(case,observations,{"reference_errors":case["reference_errors"],"issue":case["issue"]})
    check_rejection(observations["reference"],"reference")
    for method in ENGINES:
        check_rejection(observations[method],"product",case["issue"],method)


@pytest.mark.parametrize("case", REPRESENTATION_CASES, ids=lambda case: case["id"])
def test_representation(case,record):
    observations = {"reference":observe(reference(),case["inputs"])}
    observations.update({method:observe(engine,case["inputs"]) for method,engine in ENGINES.items()})
    record(case,observations,{"reference_accepts":case["reference_accepts"],"product_accepts":case["product_accepts"],"issue":case["issue"]})
    for source, accepts in [("reference",case["reference_accepts"]),("SAW",case["product_accepts"]),("TOPSIS",case["product_accepts"])]:
        observation=observations[source]
        assert observation["input_unchanged"]
        if accepts:
            assert observation["error_class"] is None
            assert observation["value"] is not None
        else:
            check_rejection(observation,"reference" if source=="reference" else "product",case["issue"],source)
