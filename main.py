
from pydantic import BaseModel, ConfigDict
import json

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

def main():
    test_cases = load_test_cases("test_cases.json")
    print(test_cases)


if __name__ == "__main__":
    main()
