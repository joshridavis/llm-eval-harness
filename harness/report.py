def _pct(x):
    return "–" if x is None else f"{round(x * 100)}%"


def render_report(baseline, candidate, diffs):
    cand = {c["id"]: c for c in candidate["cases"]}
    bad = sum(d["status"] in ("REGRESSION", "MISSING") for d in diffs)
    lines = [
        f"# Eval report: {candidate['suite']}",
        "",
        f"- Baseline: prompt {baseline['prompt']}, model {baseline['model']}, {baseline['runs_per_case']} runs per case",
        f"- Candidate: prompt {candidate['prompt']}, model {candidate['model']}, {candidate['runs_per_case']} runs per case",
        "",
        f"**Result: {bad} regression(s)**" if bad else "**Result: no regressions**",
        "",
        "| Case | Baseline | Candidate | Change | Status | Candidate verdict | Candidate confidence |",
        "|---|---|---|---|---|---|---|",
    ]
    for d in diffs:
        c = cand.get(d["id"])
        change = "–" if d["delta"] is None else f"{round(d['delta'] * 100):+d} pts"
        verdict = c["verdict"] if c else "–"
        conf = f"{c['confidence_mean']:.2f} ± {c['confidence_stdev']:.2f}" if c else "–"
        lines.append(f"| {d['id']} | {_pct(d['baseline'])} | {_pct(d['candidate'])} | {change} "
                     f"| {d['status']} | {verdict} | {conf} |")
    return "\n".join(lines) + "\n"