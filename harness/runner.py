import statistics
from dataclasses import asdict
from datetime import datetime, timezone

from harness.model import call_model
from harness.scoring import run_checks, score_run


def verdict(pass_rate):
    if pass_rate == 1.0:
        return "STABLE_PASS"
    if pass_rate == 0.0:
        return "STABLE_FAIL"
    return "FLAKY"


def run_case(case, suite, model, judge_model, runs, call=call_model):
    records = []
    for _ in range(runs):
        output = call(suite.prompt, case.input, model)
        results = run_checks(output, case.checks, suite.schema, judge_model, call)
        score = score_run(results)
        records.append({
            "output": output,
            "passed": score.passed,
            "confidence": score.confidence,
            "checks": [asdict(r) for r in results],
        })
    pass_rate = round(sum(r["passed"] for r in records) / runs, 2)
    confidences = [r["confidence"] for r in records]
    return {
        "id": case.id,
        "pass_rate": pass_rate,
        "confidence_mean": round(statistics.mean(confidences), 2),
        "confidence_stdev": round(statistics.pstdev(confidences), 2),
        "verdict": verdict(pass_rate),
        "runs": records,
    }


def run_suite(suite, prompt_version, model, judge_model, runs, call=call_model):
    return {
        "suite": suite.name,
        "prompt": prompt_version,
        "model": model,
        "judge_model": judge_model,
        "runs_per_case": runs,
        "created": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "cases": [run_case(c, suite, model, judge_model, runs, call) for c in suite.cases],
    }