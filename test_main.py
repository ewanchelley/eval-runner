from unittest.mock import MagicMock
from anthropic.types import TextBlock

from main import apply_check, call_model


def test_contains_check_passes_when_expected_present() -> None:
    assert apply_check("The capital is Paris.", "contains", "Paris")


def test_contains_check_is_case_insensitive() -> None:
    assert apply_check("the capital is paris", "contains", "Paris")


def test_contains_check_fails_when_expected_absent() -> None:
    assert apply_check("The capital is Berlin.", "contains", "Paris") is False


def test_unknown_check_type_fails() -> None:
    assert apply_check("anything", "nonsense", "anything") is False


def test_exact_match_passes_on_exact_response() -> None:
    assert apply_check("Paris", "exact_match", "Paris")


def test_exact_match_is_case_insensitive() -> None:
    assert apply_check("paris", "exact_match", "Paris")


def test_exact_match_tolerates_surrounding_whitespace() -> None:
    assert apply_check("  Paris\n", "exact_match", "Paris")


def test_exact_match_fails_when_model_pads_the_answer() -> None:
    assert apply_check("The capital is Paris.", "exact_match", "Paris") is False


def test_exact_match_fails_on_trailing_punctuation() -> None:
    assert apply_check("Paris.", "exact_match", "Paris") is False


def test_call_model() -> None:
    prompt = "What is the capital of France?"

    text_block = TextBlock(type="text", text="Paris", citations=None)

    mock_message = MagicMock()
    mock_message.content = [text_block]

    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_message

    assert call_model(mock_client, prompt) == "Paris"
