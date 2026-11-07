from harness.assertions import CheckResult
from harness.scoring import run_checks, score_run

SCHEMA = {"type": "object", "required": ["comment"]}


def ok(check, score=1.0):
    return CheckResult(check, True, score, "")


def bad(check, score=0.0):
    return CheckResult(check, False, score, "")


def test_all_passed_full_confidence():
    s = score_run([ok("schema"), ok("contains"), ok("judge")])
    assert s.passed is True and s.confidence == 1.0


def test_weighted_confidence():
    # schema 3 x 1.0 + judge 2 x 0.6 + similarity 1 x 0.5 = 4.7 / 6 = 0.78
    s = score_run([ok("schema"), ok("judge", 0.6), bad("similarity", 0.5)])
    assert s.passed is False and s.confidence == 0.78


def test_schema_failure_zeroes_the_run():
    s = score_run([bad("schema"), ok("contains"), ok("judge")])
    assert s.passed is False and s.confidence == 0.0


def test_run_checks_dispatches_by_type():
    output = '{"comment": "Please add the steps."}'
    checks = [{"type": "schema"},
              {"type": "contains", "field": "comment", "any_of": ["steps"]},
              {"type": "refusal", "field": "comment", "expect": False}]
    results = run_checks(output, checks, SCHEMA, "judge-model")
    assert [r.check for r in results] == ["schema", "contains", "refusal"]
    assert all(r.passed for r in results)


def test_run_checks_on_non_json_output():
    checks = [{"type": "schema"}, {"type": "contains", "field": "comment", "any_of": ["x"]}]
    results = run_checks("APPROVED", checks, SCHEMA, "judge-model")
    assert [r.passed for r in results] == [False, False]
