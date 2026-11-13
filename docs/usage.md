# Using the harness

## What gets installed

```
.claude/
  CLAUDE.md            the contract: seats, modes, when to escalate (loads next to your own CLAUDE.md)
  settings.json        the two hooks (merged into yours if you have one)
  agents/              advisor (Fable 5.2, read-only), builder (Opus 5.5), scout (Haiku 5.5), verifier (Opus 5.5)
  hooks/jev_route.py   UserPromptSubmit: which seat gets this task
  hooks/jev_done.py    Stop: is the goal met
  checks.sh            prints the evidence the done gate reads
  GOAL.template.md     the finish line, written as evidence
  commands/            /orchestrate /ruled-out /reverse-brief /one-rule /audit-harness
STATE.md               what is done, what was ruled out
receipts/              one short file per finished piece
```

## Jev access

The hooks call TypeSafe directly (`https://api.typesafe.ai`), so they work on any network.
Export one variable in the shell that starts `claude`:

```bash
export TYPESAFE_API_KEY=...   # from typesafe.ai; keep it out of git
```

The hooks use the SDK's default model, `jev-latest` (`jev-1.14.0` on 2026-11-13). A TypeSafe key
can list `jev-latest` and `jev-preview` only, so do not pin a numbered version. When you tune the
0.9 and 0.5 thresholds, note which version `jev-latest` was at the time: a new release can move the calibration.

## Ordinary days: advisor mode

Run `claude` as usual (Opus 5.5 drives). Each prompt gets one `ROUTE` line:

| Jev says (at 0.9 or more) | Driver does |
|---|---|
| lookup | sends it to the scout |
| build | sends it to the builder, skips the advisor |
| hard | calls the advisor before it plans |
| big | switches to orchestrator mode: briefs first, then waits for you |
| other, unsure, or Jev down | calls the advisor before it plans |

When you are stuck, run `/ruled-out`. It sends the advisor your goal, your attempts and your ruled-out list.

## The big job: orchestrator mode

1. `claude --model fable` (Fable 5.2 drives).
2. Copy `.claude/GOAL.template.md` to `GOAL.md`. Write each "done means" line as something a script can print.
3. Add one `check <command>` line per condition to `.claude/checks.sh`.
4. `/orchestrate <goal>`: approve the briefs. Builders build, the verifier checks each piece, and STATE.md records the result.
5. `/goal "everything in GOAL.md is true, stop after 5 tries"`.

The done gate runs `checks.sh` each time Claude tries to stop, then asks Jev one yes/no
question about the output:

| Result | Gate |
|---|---|
| checks fail | blocks, and gives Claude the failing output |
| Jev at 0.9 or more | lets Claude stop |
| Jev from 0.5 to 0.9, or Jev unavailable | lets Claude stop and writes `REVIEW.md` for you |
| Jev under 0.5 | blocks |
| 5 blocks in a row | lets Claude stop and writes `REVIEW.md` (the brake) |

Delete `GOAL.md` when the run is done. The gate is active only while that file exists.

## Keeping it sharp

| When | Run | Leaves behind |
|---|---|---|
| right after a hard solve | `/reverse-brief` | `.claude/skills/<name>/SKILL.md` for a smaller model |
| after each long run | `/one-rule` | one new line in `.claude/CLAUDE.md` |
| weekly | `/audit-harness` | a ranked list of decisions that a Jev gate could make |

These three commands run on Fable 5.2 (`model: fable` in their frontmatter). Each one shows
you its change first and saves nothing until you confirm.

## The ruled-out prompt for a plain chat

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

## Five ways to waste Fable 5.2

1. Fable 5.2 drives everything. Start at Opus 5.5 and go up only when the task needs it.
2. The advisor can edit. With write access it starts to fix things, and you lose the outside view.
3. Briefs with no "done when". Without a finish line, a builder returns a confident paragraph, not a command and its output.
4. The builder grades its own work. Give each result to the verifier, with a fresh context.
5. A gate approves the irreversible. Deletes, pushes, deploys and spending always come back to you.
