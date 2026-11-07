from dataclasses import dataclass

from harness.assertions import (
    CheckResult, get_field, check_schema, check_contains,
    check_refusal, check_similarity, check_judge,
)
from harness.model import call_model

WEIGHTS = {"schema": 3, "contains": 1, "refusal": 1, "similarity": 1, "judge": 2}


@dataclass
class RunScore:
    passed: bool
    confidence: float


def run_checks(output, checks, schema, judge_model, call=call_model):
    results = []
    for check in checks:
        kind = check["type"]
        if kind == "schema":
            results.append(check_schema(output, schema, check.get("require")))
            continue
        try:
            text = get_field(output, check.get("field"))
        except ValueError as e:
            results.append(CheckResult(kind, False, 0.0, f"no JSON: {e}"))
            continue
        if kind == "contains":
            results.append(check_contains(text, check.get("any_of"), check.get("all_of"), check.get("none_of")))
        elif kind == "refusal":
            results.append(check_refusal(text, check["expect"]))
        elif kind == "similarity":
            results.append(check_similarity(text, check["reference"], check["min"]))
        elif kind == "judge":
            results.append(check_judge(text, check["criteria"], check["min"], judge_model, call))
    return results


def score_run(results):
    if not results:
        raise ValueError("no check results")
    if any(r.check == "schema" and not r.passed for r in results):
        return RunScore(False, 0.0)
    total = sum(WEIGHTS[r.check] for r in results)
    confidence = round(sum(WEIGHTS[r.check] * r.score for r in results) / total, 2)
    return RunScore(all(r.passed for r in results), confidence)