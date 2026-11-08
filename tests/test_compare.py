from harness.compare import compare, has_regression


def run(**pass_rates):
    return {"cases": [{"id": k, "pass_rate": v} for k, v in pass_rates.items()]}


def statuses(diffs):
    return {d["id"]: d["status"] for d in diffs}


def test_one_run_out_of_five_is_noise():
    diffs = compare(run(a=1.0, b=0.6), run(a=0.8, b=0.8))
    assert statuses(diffs) == {"a": "SAME", "b": "SAME"}
    assert not has_regression(diffs)


def test_two_runs_out_of_five_is_a_regression():
    diffs = compare(run(a=1.0), run(a=0.6))
    assert statuses(diffs) == {"a": "REGRESSION"}
    assert diffs[0]["delta"] == -0.4
    assert has_regression(diffs)


def test_improvement():
    assert statuses(compare(run(a=0.2), run(a=1.0))) == {"a": "IMPROVED"}


def test_missing_case_counts_as_regression():
    diffs = compare(run(a=1.0, b=1.0), run(a=1.0))
    assert statuses(diffs) == {"a": "SAME", "b": "MISSING"}
    assert has_regression(diffs)


def test_new_case_is_not_a_regression():
    diffs = compare(run(a=1.0), run(a=1.0, z=0.0))
    assert statuses(diffs) == {"a": "SAME", "z": "NEW"}
    assert not has_regression(diffs)

