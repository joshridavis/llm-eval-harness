from harness.cases import Case, Suite
from harness.runner import run_case, run_suite, verdict

SUITE = Suite("demo", "system prompt", {"type": "object", "required": ["comment"]}, [])
CASE = Case("c1", "bug text", [{"type": "schema"}])
GOOD = '{"comment": "ok"}'


def scripted(*outputs):
    queue = list(outputs)

    def call(prompt, user_input, model):
        return queue.pop(0)
    return call


def test_verdicts():
    assert verdict(1.0) == "STABLE_PASS"
    assert verdict(0.0) == "STABLE_FAIL"
    assert verdict(0.6) == "FLAKY"


def test_flaky_case():
    result = run_case(CASE, SUITE, "m", "j", 5, scripted(GOOD, GOOD, "nope", GOOD, "nope"))
    assert result["pass_rate"] == 0.6
    assert result["verdict"] == "FLAKY"
    assert result["confidence_mean"] == 0.6
    assert result["confidence_stdev"] == 0.49
    assert len(result["runs"]) == 5
    assert result["runs"][2]["output"] == "nope"


def test_stable_pass_has_zero_variance():
    result = run_case(CASE, SUITE, "m", "j", 3, scripted(GOOD, GOOD, GOOD))
    assert (result["verdict"], result["confidence_stdev"]) == ("STABLE_PASS", 0.0)


def test_run_suite_records_settings():
    suite = Suite("demo", "p", SUITE.schema, [CASE, Case("c2", "x", [{"type": "schema"}])])
    result = run_suite(suite, "v1", "model-a", "judge-b", 2, scripted(GOOD, GOOD, "x", "x"))
    assert (result["suite"], result["prompt"], result["model"]) == ("demo", "v1", "model-a")
    assert (result["judge_model"], result["runs_per_case"]) == ("judge-b", 2)
    assert [c["verdict"] for c in result["cases"]] == ["STABLE_PASS", "STABLE_FAIL"]
