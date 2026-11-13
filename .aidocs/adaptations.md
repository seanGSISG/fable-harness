# Changes from the source articles

Sources: AnnatarXBT's "Claude Fable 5.2 Harness Guide" (https://x.com/AnnatarXBT/status/2121094242135167033)
and the done gate in Mr_Buzzoni's "Loop Engineering Meets Jev Engineering"
(https://x.com/polydao/article/2103689373774483815). Everything in this table was checked on 2026-11-13 against
Claude Code 2.1.323 and typesafe-sdk 0.7.5.

| Change | Why |
|---|---|
| Wrote `builder.md` and `scout.md` | The article names these agents but gives no text for them |
| Kept `model: fable` | It is a valid alias in Claude Code 2.1.323 (no full model ID needed) |
| Hooks use the SDK default model (`jev-latest`), not a hard-coded `jev-1.13.0` | On 2026-11-13 a direct TypeSafe key lists only `jev-latest` and `jev-preview`, and `jev-latest` was `jev-1.14.0` |
| Hooks call `api.typesafe.ai` directly, not a self-hosted gateway | The harness must work off the home network. Only `TYPESAFE_API_KEY` is needed |
| Hooks run with `uv run --script` and PEP 723 dependencies | Then the target repo needs no Python env, and `typesafe-sdk` is installed and cached on the first run |
| Both hooks catch Jev errors | The article's code crashes without a key. Route gate: an error routes up to the advisor (the article's own rule for "unsure"). Done gate: an error writes REVIEW.md |
| The done gate is active only while `GOAL.md` exists, and the template ships as `.claude/GOAL.template.md` | The article's Stop hook runs on every stop, so ordinary advisor-mode sessions would be blocked by a placeholder goal |
| Added `.claude/checks.sh` | Buzzoni's hook needs it. The article's map leaves it out. The template fails until you edit it |
| The done gate writes REVIEW.md at the push cap | The original stops silently after 5 pushes, so a run with known failing checks could look finished |
| The block reason includes the last 2000 characters of failing output | Claude sees what failed without running the checks again |
| `checks.sh` timeout of 540 s, hook timeout of 600 s | The default hook timeout (60 s) is shorter than many test suites |
| Prompts 3, 4, 7, 8 and 9 are slash commands | They are usable in one keystroke. Prompts 7 to 9 set `model: fable`, because the article calls them Fable jobs |
| `/ruled-out` fills the brief from the session and sends it to the advisor | Prompt 3 was written for a plain chat. The verbatim text is also in `docs/usage.md` |
| `verifier.md` adds "Edit nothing" | It has Bash access, and a verifier that fixes code is grading its own work |
| `/goal` is used as is | It is a built-in Claude Code command ("keep working until the condition is met") |
