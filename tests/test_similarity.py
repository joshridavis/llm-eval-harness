from harness.assertions import check_similarity


def test_identical_text_scores_one():
    result = check_similarity("Please add the steps to reproduce.", "Please add the steps to reproduce.", 0.9)
    assert result.check == "similarity"
    assert result.passed and result.score >= 0.99


def test_same_meaning_scores_higher_than_unrelated():
    ask = "Please add the exact steps you took."
    close = check_similarity(ask, "Could you list the steps to reproduce the bug?", 0.0).score
    far = check_similarity(ask, "The weather in Paris is sunny today.", 0.0).score
    assert close > far


def test_unrelated_text_fails_the_threshold():
    result = check_similarity("Please add the exact steps you took.", "The weather in Paris is sunny today.", 0.45)
    assert result.passed is False
    assert 0.0 <= result.score <= 1.0
