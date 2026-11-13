# fable-harness

A drop-in harness for [Claude Code](https://docs.claude.com/en/docs/claude-code) that gives each
model one job. Fable 5.2 advises or orchestrates, Opus 5.5 builds and verifies, and Haiku 5.5
looks things up. [Jev](https://typesafe.ai), a small model that only makes decisions, handles
the yes/no and pick-one calls between them: which seat gets each prompt, and whether a long run
is really done.

## How it works

| Seat | Model | Does | Never does |
|---|---|---|---|
| Advisor | Fable 5.2 | reviews plans, names the wrong assumption | edits files |
| Orchestrator | Fable 5.2 | splits a big job into briefs, merges results | builds the pieces |
| Builder | Opus 5.5 | writes and tests code from a brief | changes the plan |
| Verifier | Opus 5.5, fresh context | tries to break each finished piece | edits files |
| Scout | Haiku 5.5 | searches and summarizes | makes judgment calls |
| Gate | Jev | routes prompts, decides when a run is done | writes a word |

Two hooks do the gating:

- **Route gate** (`UserPromptSubmit`). Before Claude sees a prompt, Jev classifies it as lookup,
  build, hard or big. The hook then adds one line that names the seat. If Jev is less than 90% sure,
  the prompt goes to the advisor.
- **Done gate** (`Stop`). During a long run, the hook runs your checks each time Claude tries to stop.
  Jev then decides whether the output proves every line of `GOAL.md`. Claude keeps working until it
  does. The gate gives up after 5 tries, and if Jev is unsure it leaves a `REVIEW.md` for you.

## Install

```bash
git clone https://github.com/seanGSISG/fable-harness
cd fable-harness
uv run install.py /path/to/your/repo    # or: just install /path/to/your/repo
export TYPESAFE_API_KEY=...              # from typesafe.ai
```

The installer never overwrites a file. If your repo already has a `.claude/settings.json`, it
adds the two hooks to that file. You can run it again safely.

**Requirements:** Claude Code with access to Fable 5.2, and [uv](https://docs.astral.sh/uv/) on
your `PATH` (the hooks run with `uv run --script`). The Jev key is optional. Without it, every
prompt goes to the advisor, and every finished run goes to `REVIEW.md` for a human to check.

## Use

- **Ordinary work:** run `claude` as usual. A `ROUTE (...)` line tells the driver which seat to use.
- **A big job:** start with `claude --model fable`, then copy `.claude/GOAL.template.md` to
  `GOAL.md` and fill in its checks. Run `/orchestrate <goal>`, then
  `/goal "everything in GOAL.md is true"`. Delete `GOAL.md` when the job is done.
- **Stuck:** `/ruled-out` sends the advisor your goal, your attempts and what you have ruled out.
- **Improving the harness:** `/reverse-brief` turns a hard fix into a skill, `/one-rule` adds one
  lesson to the contract, and `/audit-harness` finds decisions that a gate could make.

The full guide is [docs/usage.md](docs/usage.md).

## Development

```bash
just test    # gate logic and installer
just lint    # ruff + ty
```

## Credits

Built from AnnatarXBT's
[Claude Fable 5.2 Harness Guide](https://x.com/AnnatarXBT/status/2121094242135167033). The done
gate is adapted from Mr_Buzzoni's
[Loop Engineering Meets Jev Engineering](https://x.com/polydao/article/2103689373774483815).
The agent and command prompts follow those articles. Every change from the originals, and its
reason, is listed in [.aidocs/adaptations.md](.aidocs/adaptations.md).

## License

[MIT](LICENSE)
