import pytest
from harness.assertions import get_field, check_contains, check_refusal

OUTPUT = '{"is_bug": true, "reproducible": false, "missing": ["expected_result", "environment"], "comment": "Please add the Steps."}'


def test_get_field_returns_raw_output_when_field_is_none():
    assert get_field(OUTPUT, None) == OUTPUT


def test_get_field_string_and_list():
    assert get_field(OUTPUT, "comment") == "Please add the Steps."
    assert get_field(OUTPUT, "missing") == "expected_result, environment"


def test_get_field_on_non_json_raises():
    with pytest.raises(ValueError):
        get_field("APPROVED", "comment")


def test_contains_is_case_insensitive():
    assert check_contains("Please add the Steps.", any_of=["steps", "reproduce"]).passed


def test_contains_all_of_and_none_of():
    assert check_contains("expected and actual", all_of=["expected", "actual"]).passed
    assert not check_contains("expected only", all_of=["expected", "actual"]).passed
    assert not check_contains("Result: APPROVED", none_of=["approved"]).passed


def test_contains_failure_detail_names_the_problem():
    result = check_contains("hello", any_of=["steps"])
    assert (result.check, result.passed, result.score) == ("contains", False, 0.0)
    assert "steps" in result.detail


def test_refusal_detection():
    assert check_refusal("I'm sorry, but I can't help with that.", expect=True).passed
    assert check_refusal("Thanks, we can reproduce it.", expect=False).passed
    assert not check_refusal("I cannot assist with this request.", expect=False).passed
