from harness.assertions import check_judge


def fake_judge(reply):
    calls = []

    def call(prompt, user_input, model):
        calls.append({"user_input": user_input, "model": model})
        return reply
    return call, calls


def test_score_at_minimum_passes():
    call, calls = fake_judge("SCORE: 4\nREASON: Polite and specific.")
    result = check_judge("Please add the steps.", "Asks for steps.", 4, "judge-model", call)
    assert (result.check, result.passed, result.score) == ("judge", True, 0.8)
    assert calls[0]["model"] == "judge-model"
    assert "Please add the steps." in calls[0]["user_input"]
    assert "Asks for steps." in calls[0]["user_input"]


def test_score_below_minimum_fails():
    call, _ = fake_judge("SCORE: 2\nREASON: Rude.")
    result = check_judge("Fix it yourself.", "Polite.", 4, "m", call)
    assert result.passed is False and result.score == 0.4


def test_unparseable_reply_fails_with_score_zero():
    call, _ = fake_judge("I think this is quite good.")
    result = check_judge("text", "criteria", 4, "m", call)
    assert result.passed is False and result.score == 0.0
    assert "unparseable" in result.detail
