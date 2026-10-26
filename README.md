# Multi-Step Reasoning Agent with Self-Checking

## Overview

A Python-based reasoning agent that solves supported structured word problems through three phases:

1. **Planner** — identifies the problem type and creates a concise plan.
2. **Executor** — calculates the proposed answer using deterministic Python logic.
3. **Verifier** — independently validates the result and rejects invalid solutions.

The agent returns a JSON object containing the final answer, status, user-facing explanation, execution plan, verification checks, and retry count.

## Features

- CLI interface for interactive questions.
- Structured JSON responses.
- Separate planner, executor, and verifier functions.
- Bounded retries when execution or verification fails.
- Deterministic arithmetic and time calculations.
- Automated tests and JSON Lines example logs.
- No external packages or API keys required.

## Project Structure

```text
multi_step_reasoning_agent/
├── agent.py
├── prompts.py
├── test_agent.py
├── example_logs.jsonl
└── README.md
```

## Requirements

- Python 3.9 or later

## Run the Agent

```bash
python3 agent.py
```

Enter a question and read the JSON response. Type `exit` to stop.

## Run Tests

```bash
python3 test_agent.py
```

The test script executes the test cases, prints their results, and saves the outputs to `example_logs.jsonl`.

## Supported Problems

- Journey durations, including journeys crossing midnight.
- Simple apple-count arithmetic with a specified multiplier.
- Meeting-slot selection based on required duration.

Questions outside these supported formats return a failure response rather than a guessed answer.

## Prompt Documentation

The prompt templates are maintained separately in `prompts.py`. Each prompt has a specific responsibility to keep the agent modular, easier to debug, and easier to extend.

### 1. Why I Designed the Prompts This Way

**Planner Prompt**

The planner breaks a word problem into smaller, well-defined steps before attempting to solve it. This prevents the agent from jumping directly to an answer without identifying the required operations.

The prompt specifies the expected problem type, execution steps, and validation requirements. Examples involving time differences, arithmetic, and meeting-slot constraints help define the expected planning behavior.

**Executor Prompt**

The executor follows the plan and produces the proposed answer along with intermediate values and a short explanation. The prompt emphasizes structured results, explicit calculations, and avoiding assumptions when information is missing.

For arithmetic and time calculations, deterministic Python functions are used instead of relying on an LLM to perform calculations. This improves reproducibility and reduces arithmetic errors.

**Verifier Prompt**

The verifier is designed to check the proposed solution against the original question rather than simply accepting the executor's output. It checks calculations, relevant constraints, and consistency.

The agent retries when execution or verification fails, up to a configured limit. If it cannot produce a verified result, it returns a failure response rather than presenting an unverified answer as correct.

**Overall design decision:** Separate prompts and responsibilities make it easier to test each phase independently and replace individual components without redesigning the entire agent.

### 2. What I Tried That Didn't Work Well

During the initial implementation, I chose a lightweight, rule-based approach to finish a working prototype quickly without requiring API credentials or external dependencies.

This approach has several limitations:

- **Rule-based question detection:** Identifying problem types using keywords works for the included examples but may fail when the same question is phrased differently.
- **Pattern-based extraction:** Regular expressions are convenient for extracting numbers and times, but they do not understand every natural-language expression or ambiguous question.
- **Limited problem coverage:** The current executor supports selected arithmetic, journey-duration, and meeting-slot problems rather than general mathematical and logical reasoning.
- **Verification limitations:** Basic recalculation can detect incorrect values, but checking only the validity of selected time slots does not guarantee that every suitable slot was found. Completeness must also be checked.
- **Prompt templates are not executed by an LLM:** The current implementation stores separate planner, executor, and verifier prompts, but the working prototype uses deterministic Python logic rather than sending those prompts to a live model.
- **Limited recovery behavior:** Retrying the same deterministic operation is unlikely to fix an unsupported question. A more advanced implementation should use verification feedback to correct the plan or execution.

These trade-offs were accepted to prioritize a runnable prototype, clear component separation, predictable behavior, and a testable agent loop.

### 3. What I Would Improve With More Time

**Integrate a real LLM**

Connect an LLM provider through a configurable interface so the planner can interpret varied questions and generate structured plans. The executor could use the model for tasks that require language understanding while keeping calculations in Python.

**Use structured output validation**

Introduce Pydantic models to validate planner output, executor results, and verifier responses. This would reduce malformed JSON and ensure required fields have the correct types.

**Strengthen independent verification**

Implement a verifier that independently recalculates numerical results and checks both correctness and completeness. For meeting slots, it should compare the complete set of qualifying slots with the executor's selected slots.

**Implement feedback-driven retries**

Instead of repeating the same deterministic operation, pass verification errors back to the planner or executor. Each retry should attempt a meaningful correction, with a strict retry limit to avoid infinite loops.

**Expand problem coverage**

Add support for ratios, percentages, unit conversions, multiple constraints, date arithmetic, and more complex multi-step logic problems. Ambiguous questions should trigger clarification or a controlled failure.

**Improve evaluation**

Build a larger test dataset containing normal, boundary, ambiguous, and adversarial questions. Track accuracy, verification success rate, retry frequency, failure rate, and execution time.

**Improve observability and interface**

Add structured logging, clearer error categories, and an optional FastAPI endpoint that accepts a question and returns the same JSON response schema.

### Conclusion

The prototype demonstrates the core Planner → Executor → Verifier workflow with structured JSON output, deterministic calculations, bounded retries, and automated tests. The next step would be to integrate a real LLM and strengthen feedback-driven recovery and independent verification while retaining deterministic tools for calculations.



## Implementation Note

The current version uses a rule-based mock implementation rather than a live LLM. The prompt definitions document the intended LLM behavior, while deterministic Python functions perform planning, execution, and verification.

This keeps the baseline reproducible, cost-free, and easy to run locally. The prompt templates are not currently sent to an LLM API.

## Assumptions and Limitations

- Input times use 24-hour `HH:MM` notation.
- Overnight journeys are interpreted as crossing midnight.
- Meeting slots must begin and end on the same day.
- Supported arithmetic is limited to the implemented apple-count pattern.
- Natural-language parsing is rule-based and does not support every phrasing.
- Verification covers the implemented constraints, not arbitrary mathematical proofs.

## Future Improvements

- Integrate an LLM provider behind a configurable interface.
- Add structured output validation with Pydantic.
- Expand the question parser to handle more arithmetic and logic problems.
- Strengthen independent verification to check completeness as well as correctness.
- Add adversarial tests, retry diagnostics, and evaluation metrics.
- Add confidence scoring and an HTTP API.
