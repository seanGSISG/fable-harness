#!/usr/bin/env -S uv run --quiet --script
# /// script
# requires-python = ">=3.12"
# dependencies = ["typesafe-sdk>=0.7.5"]
# ///
"""Stop hook (the done gate): keeps Claude working until everything in GOAL.md is true.

Active only while GOAL.md exists at the project root; delete GOAL.md to end the run.
Exact rules stay in code: the push cap is a counter, and failing checks need no model.
When .claude/checks.sh exits 0, Jev answers one Noul question: does the output show
evidence for every condition in GOAL.md?

    checks fail          -> keep going, with the failing output
    Jev >= 0.9           -> stop
    Jev 0.5-0.9, or down -> stop and write REVIEW.md for a human
    Jev < 0.5            -> keep going
    5 pushes in a row    -> stop and write REVIEW.md (the brake)

Adapted from Mr_Buzzoni's jev_done.py: https://x.com/polydao/article/2103689373774483815
Needs TYPESAFE_API_KEY; calls api.typesafe.ai directly with the SDK default model, jev-latest.
"""

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Literal

from typesafe_sdk import Noul, NoulAnswer, TypeSafeClient

MAX_PUSHES = 5
DONE = 0.9
UNSURE = 0.5
CHECKS_TIMEOUT_S = 540  # the hook timeout in settings.json is 600

GOAL = Path("GOAL.md")
CHECKS = Path(".claude/checks.sh")
COUNTER = Path(".claude/.pushes")
REVIEW = Path("REVIEW.md")

Action = Literal["fix", "continue", "review", "stop"]


def decide(checks_rc: int, noul: float | None) -> Action:
    """Pick the next step from the checks' exit code and Jev's yes-probability (None = no answer)."""
    if checks_rc != 0:
        return "fix"
    if noul is None:
        return "review"
    if noul >= DONE:
        return "stop"
    if noul >= UNSURE:
        return "review"
    return "continue"


def run_checks() -> tuple[int, str]:
    """Run checks.sh and return its exit code and combined output."""
    try:
        done = subprocess.run(
            ["bash", str(CHECKS)],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            timeout=CHECKS_TIMEOUT_S,
        )
    except subprocess.TimeoutExpired:
        return 124, f"{CHECKS} timed out after {CHECKS_TIMEOUT_S}s"
    return done.returncode, done.stdout


def ask_jev(goal: str, evidence: str) -> float | None:
    """Return Jev's probability that the evidence covers every goal condition, or None if Jev fails."""
    try:
        answer = (
            TypeSafeClient(timeout=10)
            .system_one(
                state={"goal": goal, "checks": evidence[-20_000:]},
                questions={
                    "done": Noul(
                        instructions="Does `checks` show evidence for every condition listed in `goal`?"
                    )
                },
            )
            .answers["done"]
        )
    except Exception:  # no key, network, rate limit: a human reviews instead
        return None
    return answer.noul if isinstance(answer, NoulAnswer) else None


def let_stop(message: str = "") -> None:
    COUNTER.unlink(missing_ok=True)
    if message:
        print(json.dumps({"systemMessage": message}))


def flag_for_review(why: str, evidence: str) -> None:
    REVIEW.write_text(f"# Done gate: review needed\n\n{why}\n\n```\n{evidence[-3000:]}\n```\n")
    let_stop(f"done gate: {why} See REVIEW.md.")


def keep_going(pushes: int, reason: str) -> None:
    COUNTER.write_text(str(pushes + 1))
    print(json.dumps({"decision": "block", "reason": reason}))


def main() -> None:
    os.chdir(os.environ.get("CLAUDE_PROJECT_DIR", "."))
    json.load(sys.stdin)  # the hook input is not needed; the counter replaces stop_hook_active
    if not GOAL.exists():
        return  # no long run active: an ordinary stop

    try:
        pushes = int(COUNTER.read_text())
    except (FileNotFoundError, ValueError):
        pushes = 0

    rc, out = run_checks()
    if pushes >= MAX_PUSHES:
        flag_for_review(f"Stopped after {MAX_PUSHES} pushes; GOAL.md is not met (checks exit {rc}).", out)
        return

    noul = ask_jev(GOAL.read_text(), out) if rc == 0 else None
    match decide(rc, noul):
        case "fix":
            keep_going(
                pushes,
                f"{CHECKS} exits {rc}. Fix the failing checks, then try to finish "
                f"again. Last output:\n{out[-2000:]}",
            )
        case "continue":
            keep_going(
                pushes,
                f"Goal not met (jev: {noul:.2f}). Compare GOAL.md with the output "
                f"of {CHECKS} and finish the missing conditions.",
            )
        case "review":
            why = "Jev was unavailable." if noul is None else f"Jev put done at {noul:.2f}."
            flag_for_review(f"Checks pass, but {why}", out)
        case "stop":
            let_stop(f"done gate: GOAL.md met (jev {noul:.2f}).")


if __name__ == "__main__":
    main()
