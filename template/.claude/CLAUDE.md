# Harness contract

This project runs a seat harness: each model has one job. A hook line that starts with
`ROUTE (` arrives next to each prompt. It names the seat for that task. Follow it.

| Seat | Model | Does | Never does |
|---|---|---|---|
| Advisor | Fable 5.2 (`advisor` subagent) | reviews plans, unblocks, names the wrong assumption | edits files |
| Orchestrator | Fable 5.2 (the main session, in orchestrator mode) | splits the job, writes briefs, merges | builds the pieces |
| Builder | Opus 5.5 (`builder` subagent) | writes and tests code | changes the plan |
| Scout | Haiku 5.5 (`scout` subagent) | searches, summarizes, compacts | makes judgment calls |
| Verifier | Opus 5.5 (`verifier` subagent, fresh context) | tries to break one finished piece | edits files |
| Gate | Jev (hooks) | routes, stops, approves | writes a single word |

## Seats
- You are the driver. Build with the builder subagent, search with scout.
- Call the advisor before a plan touching 4+ files, after 2 failed attempts, before any irreversible step.
- Send the advisor three things every time: the goal, your plan, what you ruled out and why.
- When the advisor says "proceed", proceed. Don't ask twice about the same plan.
- Write every finished piece to receipts/ with the command that proves it works.

## Modes
- **Advisor mode** (ordinary days): Opus 5.5 drives and calls the advisor when it needs a second brain.
- **Orchestrator mode** (a long job with many independent parts): start the session with
  `claude --model fable` (or `/model fable`), then run `/orchestrate <goal>`.

## Long runs
1. Copy `.claude/GOAL.template.md` to `GOAL.md`. Write each "done means" line as something a script can print.
2. In `.claude/checks.sh`, add one `check` line per condition.
3. Run `/goal "everything in GOAL.md is true, stop after 5 tries"`.
4. The done gate (Stop hook) blocks each stop until the checks pass and Jev agrees that the output covers GOAL.md.
   It stops after 5 pushes. If `REVIEW.md` appears, the user must look at it before the run counts as done.
5. When the run is done, delete `GOAL.md`. The done gate is active only while that file exists.

## Files
- `STATE.md`: what is done, what was ruled out, what is open. Update it after each merge.
- `receipts/<piece>.md`: one per finished piece, with the command that proves it works and its output.

## Always comes back to the user
Deletes of data, pushes, deploys and anything that spends money, whatever any confidence says.

## Keep the harness sharp
- `/reverse-brief` right after Fable 5.2 cracks something hard: it turns the solve into a skill.
- `/one-rule` after each long run: one new line for this file, never a page.
- `/audit-harness` once a week: it finds decisions the driver still makes that a gate could make.
- `/ruled-out` when you are stuck: it sends the advisor the goal, the attempts and the ruled-out list.
