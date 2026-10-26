
import json
from agent import solve


tests=[
    (
        "A train leaves at 14:30 and arrives at 18:05. "
        "How long is the journey?",
        "3 hours 35 minutes",
        "success",
    ),
    (
        "A train leaves at 09:00 and arrives at 10:30. "
        "How long is the journey?",
        "1 hours 30 minutes",
        "success",
    ),
    (
        "A train leaves at 23:00 and arrives at 01:00. "
        "How long is the journey?",
        "2 hours 0 minutes",
        "success",
    ),
    (
        "Alice has 3 red apples and twice as many green apples. "
        "How many apples does she have in total?",
        "9",
        "success",
    ),
    (
        "Alice has 5 red apples and twice as many green apples. "
        "How many apples does she have in total?",
        "15",
        "success",
    ),
    (
        "Alice has 0 red apples and twice as many green apples. "
        "How many apples does she have in total?",
        "0",
        "success",
    ),
    (
        "A meeting needs 60 minutes. There are free slots: "
        "09:00-09:30, 09:45-10:30, 11:00-12:00. "
        "Which slots can fit the meeting?",
        "11:00-12:00",
        "success",
    ),
    (
        "A meeting needs 30 minutes. There are free slots: "
        "09:00-09:30, 09:45-10:30, 11:00-12:00. "
        "Which slots can fit the meeting?",
        "09:00-09:30, 09:45-10:30, 11:00-12:00",
        "success",
    ),
    (
        "A meeting needs 45 minutes. There are free slots: "
        "09:00-09:30, 09:45-10:30. Which slots can fit?",
        "09:45-10:30",
        "success",
    ),
    (
        "Alice has some apples. How many does she have?",
        "Unable to solve reliably.",
        "failed",
    ),
    (
        "A meeting needs 60 minutes. There are free slots: "
        "09:00-09:30, 10:00-11:00. Which slots can fit?",
        "10:00-11:00",
        "success",
    ),
]

with open("example_logs.jsonl","w",encoding="utf-8") as log_file:
    for question,expected_answer,expected_status in tests:
        result=solve(question)

        passed=(result["answer"]==expected_answer and result["status"]==expected_status)

        record={
            "question":question,
            "result":result,
            "verifier_passed":all(check["passed"] for check in result["metadata"]["checks"]),
            "retries":result["metadata"]["retries"],
            "test_passed":passed,
        }

        log_file.write(json.dumps(record)+"\n")

        print("QUESTION:",question)
        print(json.dumps(result,indent=2))
        print("TEST PASSED:",passed)
        print("-"*60)

    print("Logs saved to example_logs.jsonl")
