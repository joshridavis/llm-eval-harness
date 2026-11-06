import json
from dataclasses import dataclass
from pathlib import Path

import yaml

CHECK_TYPES = {"schema", "contains", "refusal", "similarity", "judge"}


@dataclass
class Case:
    id: str
    input: str
    checks: list


@dataclass
class Suite:
    name: str
    prompt: str
    schema: dict
    cases: list


def load_suite(folder, prompt_version):
    folder = Path(folder)
    data = yaml.safe_load((folder / "cases.yaml").read_text(encoding="utf-8"))
    prompt = (folder / f"prompt_{prompt_version}.txt").read_text(encoding="utf-8")
    schema = json.loads((folder / "schema.json").read_text(encoding="utf-8"))
    cases = []
    seen = set()
    for c in data["cases"]:
        if c["id"] in seen:
            raise ValueError(f"duplicate case id: {c['id']}")
        seen.add(c["id"])
        for check in c["checks"]:
            if check["type"] not in CHECK_TYPES:
                raise ValueError(f"unknown check type: {check['type']}")
        cases.append(Case(c["id"], c["input"], c["checks"]))
    return Suite(data["suite"], prompt, schema, cases)