
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

def main():
    load_dotenv()
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    client = anthropic.Anthropic(api_key=api_key)
    response = call_model(client, "What is the capital of France?")
    print(response)


if __name__ == "__main__":
    main()
