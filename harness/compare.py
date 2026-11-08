def compare(baseline, candidate, threshold=0.4):
    base = {c["id"]: c for c in baseline["cases"]}
    cand = {c["id"]: c for c in candidate["cases"]}
    diffs = []
    for case_id, b in base.items():
        c = cand.get(case_id)
        if c is None:
            diffs.append({"id": case_id, "baseline": b["pass_rate"], "candidate": None,
                          "delta": None, "status": "MISSING"})
            continue
        delta = round(c["pass_rate"] - b["pass_rate"], 2)
        if delta <= -threshold:
            status = "REGRESSION"
        elif delta >= threshold:
            status = "IMPROVED"
        else:
            status = "SAME"
        diffs.append({"id": case_id, "baseline": b["pass_rate"], "candidate": c["pass_rate"],
                      "delta": delta, "status": status})
    for case_id, c in cand.items():
        if case_id not in base:
            diffs.append({"id": case_id, "baseline": None, "candidate": c["pass_rate"],
                          "delta": None, "status": "NEW"})
    return diffs


def has_regression(diffs):
    return any(d["status"] in ("REGRESSION", "MISSING") for d in diffs)