# fable-harness

This repo builds a Claude Code seat harness. `template/` is the product: `install.py` copies it
into a target repo. The `.claude/` folder of this repo is not the harness, so never put template
files there.

## Layout
- `template/`: the files that get installed. `template/.claude/CLAUDE.md` is the contract that agents read in the target repo.
- `install.py`: copies missing files, merges hooks into an existing `settings.json`, and is safe to run again.
- `tests/`: the gate decisions (`decide`, `route`), the done gate's file I/O, and the installer.
- `.aidocs/adaptations.md`: links to the two source articles, and each change made to them with its reason. Do not copy article text into the repo; link to it.
- `docs/usage.md`: the user guide.

## Commands
`just test`, `just lint` (ruff + ty), `just install <target>`.

## Rules
- The hooks run in the target repo through `uv run --script`. Their dependencies live in the PEP 723 header, and `pyproject.toml` repeats them only for tests. Change both together.
- Hooks fail open: an unreachable Jev routes up to the advisor (route gate) or writes REVIEW.md (done gate). A hook must never crash or block a prompt.
- Exact rules stay in code (counters, exit codes). Jev gets only the calls that need reading.
- When you change a template prompt, record why in `.aidocs/adaptations.md`.
- Jev access is direct to `api.typesafe.ai` with `TYPESAFE_API_KEY` only. Do not route it through a private gateway: the harness must work on any network.
- Live test: `just install` into a scratch repo, then pipe `{"prompt": "..."}` into each hook with `TYPESAFE_API_KEY` set. Then run `claude -p` there to confirm that the ROUTE line arrives.
