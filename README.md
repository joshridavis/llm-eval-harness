# llm-eval-harness

[![CI](https://github.com/joshridavis/llm-eval-harness/actions/workflows/ci.yml/badge.svg)](https://github.com/joshridavis/llm-eval-harness/actions/workflows/ci.yml)

## Why this exists

Teams shipping LLM features have no regression suite. When the prompt changes or
the model version changes, nobody finds out until a customer does. Traditional
assertions don't work: the output is different every time and still correct.

This harness applies test engineering to non-deterministic systems: property-based
assertions instead of exact matching, variance measurement instead of single runs,
and version-over-version regression detection.

## What it tests

The first suite, `bug_intake`, tests a bug-report review prompt modelled on my
production n8n workflow that asks Jira reporters for missing reproduction details.
The model returns JSON: is it a bug, is it reproducible, which details are missing,
and a short comment for the reporter.

Eight cases: a complete report, a vague report, missing expected/actual results,
missing environment, a feature request, a prompt injection, a request for another
user's password, and a report with a stack trace.

## How it works

- **Test cases are YAML:** an input plus expected properties, never an exact string.
- **Four assertion strategies:**
  - `schema`: JSON Schema validation, plus per-case rules (e.g. `reproducible` must be false)
  - `contains` / `refusal`: required or forbidden words, and refusal detection
  - `similarity`: embedding cosine similarity to a reference answer (all-MiniLM-L6-v2)
  - `judge`: a second model scores the answer 1–5 against written criteria
- **Scoring:** a run passes only if every check passes. Confidence is the weighted
  mean of the check scores (schema 3, judge 2, others 1). Invalid JSON scores 0.
- **Flakiness:** every case runs N times; every call samples a new answer.
  100% pass = `STABLE_PASS`, 0% = `STABLE_FAIL`, anything between = `FLAKY`,
  reported with the standard deviation of confidence.
- **Regression detection:** two runs are compared case by case. A drop of 2+ runs
  out of 5 is a regression, a missing case is a regression, and the command exits 1.

## Run it

Install (Windows: skip the first line, the PyPI build of torch is already CPU-only):

```
pip install torch --index-url https://download.pytorch.org/whl/cpu
pip install -r requirements.txt
```

Set your Anthropic API key as `ANTHROPIC_API_KEY`, then:

```
python -m harness run --suite bug_intake --prompt v1 --model <model-id> --judge-model <model-id> --runs 5 --out results/v1-haiku.json
python -m harness compare results/v1-haiku.json results/v2-haiku.json --report results/report.md
```

## Results

5 runs per case, Claude Sonnet 5.5 as the judge.

**Findings**

- **The gate catches a bad prompt change.** The shortened prompt v2 failed the
  schema check on every run of every case: the model's JSON no longer matched the
  contract the downstream code relies on. `compare` exits 1.
- **Haiku is flaky where Sonnet isn't.** With prompt v1, Haiku passed
  `vague-report` and `no-expected-or-actual` in 4 of 5 runs.
  REPLACE THIS SENTENCE WITH THE REASON FROM THE CHECK COMMAND.
  A single run would have reported both as passing. Sonnet passed every case on every run.

### Prompt v1 vs the shortened prompt v2 (same model)

- Baseline: prompt v1, model claude-haiku-5-5
- Candidate: prompt v2, model claude-haiku-5-5

**Result: 8 regression(s)**

| Case | Baseline | Candidate | Change | Status | Candidate verdict | Candidate confidence |
|---|---|---|---|---|---|---|
| complete-report | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| vague-report | 80% | 0% | -80 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| no-expected-or-actual | 80% | 0% | -80 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| no-environment | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| feature-request | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| prompt-injection | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| asks-for-password | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |
| report-with-stack-trace | 100% | 0% | -100 pts | REGRESSION | STABLE_FAIL | 0.00 ± 0.00 |

### Model upgrade: Haiku vs Sonnet (same prompt)

- Baseline: prompt v1, model claude-haiku-5-5
- Candidate: prompt v1, model claude-sonnet-5-5

**Result: no regressions**

| Case | Baseline | Candidate | Change | Status | Candidate verdict | Candidate confidence |
|---|---|---|---|---|---|---|
| complete-report | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |
| vague-report | 80% | 100% | +20 pts | SAME | STABLE_PASS | 0.98 ± 0.00 |
| no-expected-or-actual | 80% | 100% | +20 pts | SAME | STABLE_PASS | 0.97 ± 0.00 |
| no-environment | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |
| feature-request | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |
| prompt-injection | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |
| asks-for-password | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |
| report-with-stack-trace | 100% | 100% | +0 pts | SAME | STABLE_PASS | 1.00 ± 0.00 |

## CI

GitHub Actions runs the unit tests and replays the committed results: the build
fails if the regression gate stops flagging the known-bad prompt v2. Live model runs
stay local, so CI needs no API key.

## Design decisions

- **Properties, not strings.** Every correct answer is worded differently; the
  assertions check what must be true about it.
- **The judge is a separate, stronger model.** Its score is parsed by regex,
  and an unparseable reply fails the check instead of passing silently.
- **The regression threshold is 40 points.** With 5 runs, one run is 20 points of noise.
- **Invalid JSON zeroes the run.** Downstream code can't use it, so no partial credit.

## Author

Jonathan Davis, SDET and AI automation engineer · [LinkedIn](https://linkedin.com/in/jonathanda)