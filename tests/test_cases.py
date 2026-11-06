import pytest
from harness.cases import load_suite

SUITE = "suites/bug_intake"


def test_loads_the_bug_intake_suite():
    suite = load_suite(SUITE, "v1")
    assert suite.name == "bug_intake"
    assert len(suite.cases) == 8
    assert suite.cases[0].id == "complete-report"
    assert "Reply with JSON only" in suite.prompt
    assert suite.schema["required"] == ["is_bug", "reproducible", "missing", "comment"]


def test_every_case_has_a_schema_check():
    for case in load_suite(SUITE, "v1").cases:
        assert any(check["type"] == "schema" for check in case.checks), case.id


def test_missing_prompt_version_raises():
    with pytest.raises(FileNotFoundError):
        load_suite(SUITE, "v99")


def test_duplicate_case_id_raises(tmp_path):
    (tmp_path / "prompt_v1.txt").write_text("p", encoding="utf-8")
    (tmp_path / "schema.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cases.yaml").write_text(
        "suite: s\ncases:\n"
        "  - {id: a, input: x, checks: [{type: schema}]}\n"
        "  - {id: a, input: y, checks: [{type: schema}]}\n",
        encoding="utf-8")
    with pytest.raises(ValueError, match="duplicate case id"):
        load_suite(tmp_path, "v1")


def test_unknown_check_type_raises(tmp_path):
    (tmp_path / "prompt_v1.txt").write_text("p", encoding="utf-8")
    (tmp_path / "schema.json").write_text("{}", encoding="utf-8")
    (tmp_path / "cases.yaml").write_text(
        "suite: s\ncases:\n  - {id: a, input: x, checks: [{type: regex}]}\n",
        encoding="utf-8")
    with pytest.raises(ValueError, match="unknown check type"):
        load_suite(tmp_path, "v1")