import json
from dataclasses import dataclass

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