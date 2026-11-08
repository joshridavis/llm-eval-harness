from harness.compare import compare
from harness.report import render_report


def result(prompt, pass_rate):
    return {"suite": "bug_intake", "prompt": prompt, "model": "model-a", "runs_per_case": 5,
            "cases": [{"id": "vague-report", "pass_rate": pass_rate, "verdict": "FLAKY",
                       "confidence_mean": 0.71, "confidence_stdev": 0.18}]}


def test_report_with_a_regression():
    base, cand = result("v1", 1.0), result("v2", 0.4)
    report = render_report(base, cand, compare(base, cand))
    assert report.startswith("# Eval report: bug_intake")
    assert "- Baseline: prompt v1, model model-a, 5 runs per case" in report
    assert "**Result: 1 regression(s)**" in report
    assert "| vague-report | 100% | 40% | -60 pts | REGRESSION | FLAKY | 0.71 ± 0.18 |" in report


def test_report_without_regressions():
    base = result("v1", 1.0)
    assert "**Result: no regressions**" in render_report(base, base, compare(base, base))
