---
description: Stuck? Send the advisor the goal, the attempts and the ruled-out list, and get the untested assumption back
argument-hint: [extra context]
---
Fill in this brief from the session so far and from STATE.md. Use real commands and real
results; write "unknown" where you have nothing. Extra context from me: $ARGUMENTS

```
Goal: [ONE SENTENCE]
Evidence it's done: [COMMAND OR CHECK]
Already tried:
1. [ATTEMPT] -> [WHAT HAPPENED]
2. [ATTEMPT] -> [WHAT HAPPENED]
Ruled out: [HYPOTHESES YOU KILLED, AND HOW]

Hold the solution for now. Name the assumption I haven't tested
and the cheapest experiment that would kill it.
```

Send the filled brief to the advisor subagent. Show me its answer unchanged, then run the
experiment it names if that experiment is safe and reversible.
