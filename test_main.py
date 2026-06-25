from unittest.mock import MagicMock

from anthropic.types import TextBlock

from main import apply_deterministic_check, call_model, grade_with_model


def test_contains_check_passes_when_expected_present() -> None:
    assert apply_deterministic_check("The capital is Paris.", "contains", "Paris")


def test_contains_check_is_case_insensitive() -> None:
    assert apply_deterministic_check("the capital is paris", "contains", "Paris")


def test_contains_check_fails_when_expected_absent() -> None:
    assert apply_deterministic_check("The capital is Berlin.", "contains", "Paris") is False


def test_unknown_check_type_fails() -> None:
    assert apply_deterministic_check("anything", "nonsense", "anything") is False


def test_exact_match_passes_on_exact_response() -> None:
    assert apply_deterministic_check("Paris", "exact_match", "Paris")


def test_exact_match_is_case_insensitive() -> None:
    assert apply_deterministic_check("paris", "exact_match", "Paris")


def test_exact_match_tolerates_surrounding_whitespace() -> None:
    assert apply_deterministic_check("  Paris\n", "exact_match", "Paris")


def test_exact_match_fails_when_model_pads_the_answer() -> None:
    assert apply_deterministic_check("The capital is Paris.", "exact_match", "Paris") is False


def test_exact_match_fails_on_trailing_punctuation() -> None:
    assert apply_deterministic_check("Paris.", "exact_match", "Paris") is False


def mock_client_returning(text: str) -> MagicMock:
    # Build a mock Anthropic client whose next response is `text`
    text_block = TextBlock(type="text", text=text, citations=None)
    mock_message = MagicMock()
    mock_message.content = [text_block]
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message
    return mock_client


def test_call_model() -> None:
    mock_client = mock_client_returning("Paris")
    assert call_model(mock_client, "What is the capital of France?") == "Paris"


def test_grade_with_model_passes_on_pass_verdict() -> None:
    judge = mock_client_returning("PASS")
    assert grade_with_model(judge, "prompt", "response", "expected") is True


def test_grade_with_model_fails_on_fail_verdict() -> None:
    judge = mock_client_returning("FAIL")
    assert grade_with_model(judge, "prompt", "response", "expected") is False


def test_grade_with_model_tolerates_whitespace_and_case() -> None:
    judge = mock_client_returning("  pass\n")
    assert grade_with_model(judge, "prompt", "response", "expected") is True


def test_grade_with_model_tolerates_trailing_text_after_verdict() -> None:
    judge = mock_client_returning("PASS - the response meets the rubric")
    assert grade_with_model(judge, "prompt", "response", "expected") is True


def test_grade_with_model_fails_on_unexpected_verdict() -> None:
    judge = mock_client_returning("I'm not sure about this one")
    assert grade_with_model(judge, "prompt", "response", "expected") is False
