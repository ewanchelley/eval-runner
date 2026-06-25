from main import apply_check


def test_contains_check_passes_when_expected_present():
    assert apply_check("The capital is Paris.", "contains", "Paris")


def test_contains_check_is_case_insensitive():
    assert apply_check("the capital is paris", "contains", "Paris")


def test_contains_check_fails_when_expected_absent():
    assert apply_check("The capital is Berlin.", "contains", "Paris") is False


def test_unknown_check_type_fails():
    assert apply_check("anything", "nonsense", "anything") is False