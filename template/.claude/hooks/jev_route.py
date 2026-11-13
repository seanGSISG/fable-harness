#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["typesafe-sdk>=0.7.5"]
# ///
"""UserPromptSubmit hook: asks Jev which seat a prompt belongs to, then prints one ROUTE line.

Claude Code adds what this prints to the driver's context, next to the prompt.
It routes only when Jev is at least 90% sure. An unsure answer, "other", or an unreachable
Jev routes up to the advisor: a wrong "hard" costs one short advisor call, but a wrong
"lookup" on a hard problem costs the evening. The hook never blocks a prompt.

Needs TYPESAFE_API_KEY; calls api.typesafe.ai directly with the SDK default model, jev-latest.
"""

import json
import sys

from typesafe_sdk import Choice, ChoiceAnswer, TypeSafeClient

THRESHOLD = 0.9

CRITERIA = {
    "lookup": "Find, list, summarize or explain something that already exists",
    "build": "Write or change code with a clear spec in one area of the project",
    "hard": "Unknown cause, several failed attempts, a design decision, or a change across many parts",
    "big": "A long job that splits into many independent pieces",
    "other": "None of the above fits",
}

# "other" has no route on purpose: anything strange goes to the advisor.
ROUTES = {
    "lookup": "Use the scout subagent. Keep the answer short.",
    "build": "Use the builder subagent. Skip the advisor.",
    "hard": "Call the advisor before you plan.",
    "big": "Run this in orchestrator mode: briefs first, then wait for my confirm.",
}

UNSURE = "ROUTE (unsure): call the advisor before you plan."


def route(choice: str, confidence: float) -> str:
    """Turn one Jev answer into the ROUTE line for the driver."""
    if confidence >= THRESHOLD and choice in ROUTES:
        return f"ROUTE ({choice}, jev {confidence:.2f}): {ROUTES[choice]}"
    return UNSURE


def main() -> None:
    prompt = json.load(sys.stdin).get("prompt", "")
    try:
        answer = (
            TypeSafeClient(timeout=5)
            .system_one(
                state={"task": prompt},
                questions={
                    "seat": Choice(instructions="What kind of work does `task` ask for?", criteria=CRITERIA)
                },
            )
            .answers["seat"]
        )
        if not isinstance(answer, ChoiceAnswer):
            raise TypeError(f"expected a choice answer, got {type(answer).__name__}")
    except Exception as exc:  # no key, network, rate limit: route up, never block the prompt
        print(f"{UNSURE} (jev unavailable: {type(exc).__name__})")
        return
    print(route(answer.choice, answer.confidence))


if __name__ == "__main__":
    main()
