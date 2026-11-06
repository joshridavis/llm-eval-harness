import json
import pytest
from harness.assertions import extract_json, check_schema

SCHEMA = json.load(open("suites/bug_intake/schema.json", encoding="utf-8"))
GOOD = '{"is_bug": true, "reproducible": false, "missing": ["environment"], "comment": "Which browser?"}'


def test_extract_json_plain():
    assert extract_json(GOOD)["missing"] == ["environment"]


def test_extract_json_inside_code_fence():
    assert extract_json("```json\n" + GOOD + "\n```")["is_bug"] is True


def test_extract_json_no_object_raises():
    with pytest.raises(ValueError):
        extract_json("APPROVED")


def test_extract_json_broken_json_raises():
    with pytest.raises(ValueError):
        extract_json('{"is_bug": true,}')


def test_valid_output_passes():
    result = check_schema(GOOD, SCHEMA)
    assert (result.check, result.passed, result.score) == ("schema", True, 1.0)


def test_unknown_missing_value_fails():
    bad = GOOD.replace('"environment"', '"browser"')
    result = check_schema(bad, SCHEMA)
    assert result.passed is False and result.score == 0.0


def test_require_adds_case_rules():
    assert check_schema(GOOD, SCHEMA, {"reproducible": {"const": False}}).passed
    assert not check_schema(GOOD, SCHEMA, {"reproducible": {"const": True}}).passed
    assert check_schema(GOOD, SCHEMA, {"missing": {"contains": {"const": "environment"}}}).passed


def test_not_json_fails_with_detail():
    result = check_schema("Sure! The bug looks reproducible.", SCHEMA)
    assert result.passed is False and "no JSON" in result.detail
