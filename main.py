import json
import os
import sys

import anthropic
from anthropic.types import TextBlock
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError


class TestCase(BaseModel):
    id: str
    prompt: str
    check: str
    expected: str


class EvalResult(BaseModel):
    id: str
    passed: bool
    response: str


def load_test_cases(path: str) -> list[TestCase]:
    with open(path) as f:
        data = json.load(f)
    return [TestCase(**item) for item in data]


def call_model(client: anthropic.Anthropic, prompt: str) -> str:
    message = client.messages.create(
        model="claude-haiku-4-5",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    block = message.content[0]
    if not isinstance(block, TextBlock):
        raise ValueError(f"Expected a text response, got {type(block).__name__}")
    return block.text


def apply_deterministic_check(response: str, check: str, expected: str) -> bool:
    if check == "contains":
        return expected.lower() in response.lower()
    if check == "exact_match":
        return response.strip().lower() == expected.lower()
    return False


def grade_with_model(
    client: anthropic.Anthropic, prompt: str, response: str, expected: str
) -> bool:
    grading_prompt = f"""
        You are an LLM eval, and must grade the response of another LLM.
        The LLM was given this prompt:

        PROMPT: "{prompt}".

        It was expected to produce a response that aligns with this expectation:

        EXPECTED: "{expected}".

        The actual response the LLM gave was:

        RESPONSE: "{response}".

        Determine whether the LLM gave a satisfactory response, 
        according to the expectation. 
        If so, your response should simply be PASS, otherwise it should be FAIL.

    """
    verdict = call_model(client, grading_prompt)
    outcome = verdict.strip().upper().startswith("PASS")
    return outcome


def print_report(results: list[EvalResult]) -> None:
    for r in results:
        preview = " ".join(r.response.split())[:200]
        print(f"\n{r.id}: {'PASS' if r.passed else 'FAIL'}")
        print(f"  Response: {preview}")

    total = len(results)
    passed_count = sum(r.passed for r in results)
    print(f"\nSCORE: {passed_count}/{total} passed")


def load_test_cases_or_exit(path: str) -> list[TestCase]:
    try:
        return load_test_cases(path)
    except FileNotFoundError:
        print(f"Error: {path} not found.", file=sys.stderr)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print(f"Error: {path} is not valid JSON: {e}", file=sys.stderr)
        sys.exit(1)
    except ValidationError as e:
        print(f"Error: a test case is malformed:\n{e}", file=sys.stderr)
        sys.exit(1)


def main() -> None:
    load_dotenv(override=True)
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key is None:
        print(
            "Error: ANTHROPIC_API_KEY is not set. Add it to a .env file.",
            file=sys.stderr,
        )
        sys.exit(1)

    client = anthropic.Anthropic(api_key=api_key)

    test_cases = load_test_cases_or_exit("test_cases.json")

    results = []
    for tc in test_cases:
        response = call_model(client, tc.prompt)
        if tc.check == "model_graded":
            passed = grade_with_model(client, tc.prompt, response, tc.expected)
        else:
            passed = apply_deterministic_check(response, tc.check, tc.expected)
        results.append(EvalResult(id=tc.id, passed=passed, response=response))
    print_report(results)


if __name__ == "__main__":
    main()
