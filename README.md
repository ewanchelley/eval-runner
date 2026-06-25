# eval-runner

A minimal LLM evaluation runner. It reads a set of test cases (a prompt plus an
expected check), sends each prompt to a Claude model, applies the check to the
model's response, and prints a pass/fail report with an overall score.

It's a small, deliberately-scoped project - a "from scratch" take on the core
loop behind eval frameworks like [Inspect](https://inspect.aisi.org.uk/): load
cases → run the model → score → report.

## How it works

```
test_cases.json  →  load & validate  →  call model  →  apply check  →  report
                       (pydantic)        (Anthropic)     (scoring)      (score)
```

- **`TestCase`** / **`EvalResult`** - pydantic models that validate the test-case
  data on load and structure the results.
- **`load_test_cases`** - reads and validates the JSON test cases.
- **`call_model`** - sends a prompt to Claude and returns the text response.
- **`apply_check`** - applies a check to the response and returns pass/fail.
- **`print_report`** - prints per-case results and the overall score.

## Test cases

Test cases live in `test_cases.json` as a list of objects:

```json
[
  {
    "id": "capital-france",
    "prompt": "What is the capital of France?",
    "check": "contains",
    "expected": "Paris"
  }
]
```

| Field      | Meaning                                             |
| ---------- | --------------------------------------------------- |
| `id`       | Unique identifier for the test case                 |
| `prompt`   | The prompt sent to the model                        |
| `check`    | The check to apply to the response                  |
| `expected` | The value the check compares against                |

### Supported checks

| Check      | Passes when…                                         |
| ---------- | ---------------------------------------------------- |
| `contains` | The response contains `expected` (case-insensitive)  |

Unknown check types fail safely rather than passing silently.

## Setup

Requires [uv](https://docs.astral.sh/uv/) and an Anthropic API key.

```bash
uv sync
```

Create a `.env` file in the project root:

```
ANTHROPIC_API_KEY=sk-ant-...
```

## Usage

```bash
uv run python main.py
```

Example output:

```
capital-france: PASS
  Response: The capital of France is Paris.
sentiment: PASS
  Response: NEGATIVE

SCORE: 2/2 passed
```

## Development

The project is set up with standard Python tooling:

```bash
uv run pytest        # run the test suite (API calls are mocked - no key needed)
uv run ruff check    # lint
uv run ruff format   # format
uv run mypy .        # static type checking (strict mode)
```

The test suite mocks the Anthropic client, so it runs fast, for free, and
without network access.

## Possible extensions

- More check types (regex match, exact match, JSON-schema validation,
  model-graded / LLM-as-judge scoring)
- Configurable model and parameters per test case
- Structured output (JSON/CSV) alongside the printed report
- Concurrency for running cases in parallel
