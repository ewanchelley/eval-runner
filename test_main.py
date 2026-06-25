from unittest.mock import MagicMock

from main import apply_check, call_model


def test_contains_check_passes_when_expected_present() -> None:
    assert apply_check("The capital is Paris.", "contains", "Paris")


def test_contains_check_is_case_insensitive() -> None:
    assert apply_check("the capital is paris", "contains", "Paris")


def test_contains_check_fails_when_expected_absent() -> None:
    assert apply_check("The capital is Berlin.", "contains", "Paris") is False


def test_unknown_check_type_fails() -> None:
    assert apply_check("anything", "nonsense", "anything") is False


def test_call_model() -> None:
    prompt = "What is the capital of France?"

    mock_response = MagicMock()
    mock_response.content[0].text = "Paris"
    mock_client = MagicMock()
    mock_client.messages.create.return_value = mock_response

    assert call_model(mock_client, prompt) == "Paris"
