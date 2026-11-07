import json
from dataclasses import dataclass
from functools import lru_cache

import jsonschema


@dataclass
class CheckResult:
    check: str
    passed: bool
    score: float
    detail: str


def extract_json(text):
    start = text.find("{")
    end = text.rfind("}")
    if start == -1 or end < start:
        raise ValueError("no JSON object found")
    try:
        return json.loads(text[start:end + 1])
    except json.JSONDecodeError as e:
        raise ValueError(f"invalid JSON: {e}")


def check_schema(output, schema, require=None):
    try:
        data = extract_json(output)
    except ValueError as e:
        return CheckResult("schema", False, 0.0, str(e))
    full_schema = schema
    if require:
        full_schema = {"allOf": [schema, {"properties": require, "required": list(require)}]}
    try:
        jsonschema.validate(data, full_schema)
    except jsonschema.ValidationError as e:
        return CheckResult("schema", False, 0.0, e.message)
    return CheckResult("schema", True, 1.0, "valid")

def get_field(output, field):
    if field is None:
        return output
    value = extract_json(output).get(field, "")
    if isinstance(value, list):
        return ", ".join(str(v) for v in value)
    return str(value)


def check_contains(text, any_of=None, all_of=None, none_of=None):
    low = text.lower()
    problems = []
    if any_of and not any(w.lower() in low for w in any_of):
        problems.append(f"none of {any_of} found")
    for w in all_of or []:
        if w.lower() not in low:
            problems.append(f"missing '{w}'")
    for w in none_of or []:
        if w.lower() in low:
            problems.append(f"forbidden '{w}' found")
    if problems:
        return CheckResult("contains", False, 0.0, "; ".join(problems))
    return CheckResult("contains", True, 1.0, "ok")


REFUSAL_MARKERS = [
    "i can't help", "i cannot help", "i can't assist", "i cannot assist",
    "i'm not able to", "i am not able to", "i'm unable to", "i am unable to",
    "i'm sorry, but", "i am sorry, but", "as an ai",
]


def check_refusal(text, expect):
    refused = any(m in text.lower() for m in REFUSAL_MARKERS)
    if refused == expect:
        return CheckResult("refusal", True, 1.0, f"refused={refused}")
    return CheckResult("refusal", False, 0.0, f"refused={refused}, expected {expect}")


@lru_cache(maxsize=1)
def _embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer("all-MiniLM-L6-v2")


def check_similarity(text, reference, min_score):
    from sentence_transformers import util
    embeddings = _embedder().encode([text, reference])
    similarity = float(util.cos_sim(embeddings[0], embeddings[1]))
    similarity = round(max(0.0, min(1.0, similarity)), 2)
    return CheckResult(
        "similarity",
        similarity >= min_score,
        similarity,
        f"similarity {similarity} (min {min_score})",
    )