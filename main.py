
from pydantic import BaseModel, ConfigDict
import json
import os
from dotenv import load_dotenv
import anthropic

class TestCase(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str
    prompt: str
    check: str
    expected: str

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
    return message.content[0].text

def apply_check(response: str, check: str, expected: str) -> bool:
    if check == "contains":
        return expected.lower() in response.lower()
    return False

def main():
    load_dotenv()
    client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
    test_cases = load_test_cases("test_cases.json")
    
    results = []
    for tc in test_cases:
        response = call_model(client, tc.prompt)
        passed = apply_check(response, tc.check, tc.expected)
        results.append(passed)
        print(f"{tc.id}: {'PASS' if passed else 'FAIL'}")
    total = len(results)
    passed_count = sum(results)
    print(f"\nSCORE: {passed_count}/{total} passed")


if __name__ == "__main__":
    main()
