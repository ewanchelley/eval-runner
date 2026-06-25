# eval-runner

A minimal LLM evaluation runner. It reads a set of test cases (a prompt plus an
expected check), sends each prompt to a Claude model, applies the check to the
model's response, and prints a pass/fail report with an overall score.

## How it works

```
test_cases.json 
 →  load & validate (pydantic)
 →  call model (Anthropic) 
 →  apply check (scoring)
 →  report (final score)                                  
```

- **`TestCase`** / **`EvalResult`** - pydantic models that validate the test-case
  data on load and structure the results.
- **`load_test_cases`** - reads and validates the JSON test cases.
- **`call_model`** - sends a prompt to Claude and returns the text response.
- **`apply_deterministic_check`** - applies a string-based check (`contains`,
  `exact_match`) to the response and returns pass/fail.
- **`grade_with_model`** - applies a `model_graded` check by asking a second model
  call (the "judge") to score the response against a rubric.
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
| `expected` | The value the check compares against, or a rubric for `model_graded` |

### Supported checks

| Check          | Passes when…                                                          |
| -------------- | --------------------------------------------------------------------- |
| `contains`     | The response contains `expected` (case-insensitive)                   |
| `exact_match`  | The response equals `expected` (case-insensitive, whitespace-trimmed) |
| `model_graded` | A second model call ("judge") grades the response as meeting `expected`|

`exact_match` is stricter than `contains`: it trims surrounding whitespace and
ignores case, but does not strip punctuation or extra words. This makes it a test
of instruction-following - e.g. whether a model asked to "answer with a single
word" actually does, rather than padding the answer with a full sentence.

`model_graded` handles open-ended cases where no string match is possible (e.g.
"is this explanation correct *and* simple?", "did the model refuse this request?").
A second "judge" call is given the original prompt, the response, and the
`expected` field as a **rubric**, and asked to reply `PASS` or `FAIL`. Here
`expected` describes the grading criteria rather than a literal target string. The
judge is reliable because grading against a rubric is an easier task than solving
from scratch - though it is not infallible (model judges can exhibit self-preference,
verbosity, and position biases).

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
uv run pytest        # run the test suite (mock API calls)
uv run ruff check    # lint
uv run ruff format   # format
uv run mypy .        # static type checking (strict mode)
```

The test suite mocks the Anthropic client, so it runs fast, for free, and
without network access.

## Possible extensions

- More check types (regex match, JSON-schema validation)
- Configurable model and parameters per test case
- Structured output (JSON/CSV) alongside the printed report
- Concurrency for running cases in parallel
