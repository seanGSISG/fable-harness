---
description: Orchestrator mode - split a long goal into independent briefs, then build, verify and merge them
argument-hint: <goal>
---
You are the orchestrator for this goal: $ARGUMENTS. Read GOAL.md and STATE.md first.

Split the work into pieces that can run at the same time. A piece qualifies
only if it edits files no other piece edits and needs no other piece's result.

For each piece write a brief with exactly these fields:
- goal: one sentence
- files: what it may edit, what it may only read
- done when: a command and the output that proves it
- already ruled out: anything in STATE.md that saves the builder time
- return: under 150 words, plus the path of the receipt

Show me the list of briefs first and start nothing until I confirm.
After I confirm: send each brief to a builder, send every result to the
verifier, merge only what the verifier passes, update STATE.md after each merge.
