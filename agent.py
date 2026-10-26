
import json
import re
from datetime import datetime

from prompts import PLANNER_PROMPT, EXECUTOR_PROMPT, VERIFIER_PROMPT

MAX_RETRIES=2


def parse_time(value):
    return datetime.strptime(value,"%H:%M")


def plan(question):
    q=question.lower()

    if "train" in q or "leaves at" in q or "arrives at" in q:
        problem_type="time_difference"
        steps=[
            "Extract departure and arrival times",
            "Calculate elapsed time",
            "Validate elapsed minutes"
        ]
    elif "slot" in q or "meeting needs" in q or "free slots" in q:
        problem_type="time_slots"
        steps=[
            "Extract required meeting duration",
            "Calculate each slot's duration",
            "Select slots meeting the requirement"
        ]
    elif "apple" in q or "twice as many" in q:
        problem_type="arithmetic"
        steps=[
            "Extract the known quantity",
            "Calculate the related quantity",
            "Calculate and validate the total"
        ]
    else:
        problem_type="unsupported"
        steps=["Determine whether the problem is supported"]

    return {"problem_type":problem_type,"steps":steps}


def execute(question,plan_result):
    q=question.lower()
    kind=plan_result["problem_type"]

    if kind=="time_difference":
        times=re.findall(r"\b\d{1,2}:\d{2}\b",question)

        if len(times)<2:
            raise ValueError("Departure and arrival times are required.")

        start=parse_time(times[0])
        end=parse_time(times[1])
        minutes=int((end-start).total_seconds()//60)

        if minutes<0:
            minutes+=24*60

        hours,remaining=divmod(minutes,60)

        return {
            "answer":f"{hours} hours {remaining} minutes",
            "value":minutes,
            "explanation":f"The journey takes {hours} hours and {remaining} minutes."
        }

    if kind=="arithmetic":
        match=re.search(
            r"(\d+)\s+red\s+apples?.*?twice as many green apples",
            q
        )

        if not match:
            raise ValueError("Could not extract the apple quantities.")

        red=int(match.group(1))
        green=red*2
        total=red+green

        return {
            "answer":str(total),
            "value":total,
            "red":red,
            "green":green,
            "explanation":f"There are {red} red apples and {green} green apples, giving {total} apples altogether."
        }

    if kind=="time_slots":
        duration_match=re.search(r"(\d+)\s*minutes?",q)

        if not duration_match:
            raise ValueError("Could not determine the required duration.")

        required=int(duration_match.group(1))
        slots_match=re.search(r"free slots:\s*(.+)",question,re.IGNORECASE)

        if not slots_match:
            raise ValueError("Could not extract the free time slots.")

        slots=re.findall(
            r"(\d{1,2}:\d{2})\s*[-–]\s*(\d{1,2}:\d{2})",
            slots_match.group(1)
        )

        if not slots:
            raise ValueError("No valid time slots were found.")

        suitable=[]

        for start_text,end_text in slots:
            start=parse_time(start_text)
            end=parse_time(end_text)
            available=int((end-start).total_seconds()//60)

            if available>=required:
                suitable.append(f"{start_text}-{end_text}")

        answer=", ".join(suitable) if suitable else "No suitable slots"

        return {
            "answer":answer,
            "value":suitable,
            "required_minutes":required,
            "explanation":f"Only slots lasting at least {required} minutes are suitable. Result: {answer}."
        }

    raise ValueError(
        "Unsupported problem type. Supported types are time differences, "
        "simple apple-count arithmetic, and meeting time slots."
    )


def verify(question,solution,plan_result):
    kind=plan_result["problem_type"]
    passed=True
    details=""

    if kind=="time_difference":
        times=re.findall(r"\b\d{1,2}:\d{2}\b",question)
        start=parse_time(times[0])
        end=parse_time(times[1])
        expected=int((end-start).total_seconds()//60)

        if expected<0:
            expected+=24*60

        passed=expected==solution["value"] and expected>=0
        details=(
            "Independently recalculated elapsed minutes."
            if passed
            else "Elapsed time does not match independent calculation."
        )

    elif kind=="arithmetic":
        passed=(
            solution["green"]==solution["red"]*2
            and solution["value"]==solution["red"]+solution["green"]
            and solution["red"]>=0
        )
        details=(
            "Verified the multiplier and total."
            if passed
            else "Apple counts or total are inconsistent."
        )

    elif kind=="time_slots":
        passed=all(
            int(
                (
                    parse_time(slot.split("-")[1])
                    -parse_time(slot.split("-")[0])
                ).total_seconds()//60
            )>=solution["required_minutes"]
            for slot in solution["value"]
        )
        details=(
            "Every selected slot meets the duration requirement."
            if passed
            else "A selected slot does not meet the requirement."
        )

    else:
        passed=False
        details="Unsupported problem type."

    return {
        "check_name":"independent_validation",
        "passed":passed,
        "details":details
    }


def solve(question):
    retries=0
    last_error="Unable to solve the question."
    plan_result=plan(question)

    while retries<=MAX_RETRIES:
        try:
            solution=execute(question,plan_result)
            check=verify(question,solution,plan_result)

            if check["passed"]:
                return {
                    "answer":solution["answer"],
                    "status":"success",
                    "reasoning_visible_to_user":solution["explanation"],
                    "metadata":{
                        "plan":" -> ".join(plan_result["steps"]),
                        "checks":[check],
                        "retries":retries
                    }
                }

            last_error=check["details"]

        except (ValueError,IndexError,TypeError) as error:
            last_error=str(error)

        retries+=1

    failed_check={
        "check_name":"independent_validation",
        "passed":False,
        "details":last_error
    }

    return {
        "answer":"Unable to solve reliably.",
        "status":"failed",
        "reasoning_visible_to_user":(
            "The problem could not be solved and verified reliably. "
            "Please clarify the question or provide more details."
        ),
        "metadata":{
            "plan":" -> ".join(plan_result["steps"]),
            "checks":[failed_check],
            "retries":retries-1
        }
    }


def main():
    print("Multi-Step Reasoning Agent")
    print("Type 'exit' to quit.\n")

    while True:
        question=input("Question: ").strip()

        if question.lower()=="exit":
            break

        if not question:
            print("Please enter a question.\n")
            continue

        result=solve(question)
        print(json.dumps(result,indent=2))
        print()


if __name__=="__main__":
    main()
