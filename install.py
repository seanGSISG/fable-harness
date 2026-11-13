"""Install the harness into a target repo without overwriting anything.

Copies each file in template/ that the target is missing. If the target already has
.claude/settings.json, it adds the harness hooks to it instead of replacing it.
It also adds the done gate's push counter to .gitignore. Safe to run again.

Use: `just install <target-dir>` or `uv run install.py <target-dir>`.
"""

import json
import shutil
import sys
from pathlib import Path
from typing import Any

TEMPLATE = Path(__file__).parent / "template"
SETTINGS = Path(".claude/settings.json")
IGNORED = ".claude/.pushes"


def merge_hooks(existing: dict[str, Any], harness: dict[str, Any]) -> dict[str, Any]:
    """Return `existing` with each harness hook group added, unless its command is already there."""
    merged = json.loads(json.dumps(existing))  # deep copy
    events = merged.setdefault("hooks", {})
    for event, groups in harness["hooks"].items():
        current = events.setdefault(event, [])
        commands = {h.get("command") for g in current for h in g.get("hooks", [])}
        current.extend(g for g in groups if not any(h["command"] in commands for h in g["hooks"]))
    return merged


def install(target: Path) -> list[str]:
    """Install the harness into `target` and return one line per action taken."""
    log: list[str] = []
    for src in sorted(p for p in TEMPLATE.rglob("*") if p.is_file() and "__pycache__" not in p.parts):
        rel = src.relative_to(TEMPLATE)
        dst = target / rel
        if rel == SETTINGS and dst.exists():
            existing = json.loads(dst.read_text())
            merged = merge_hooks(existing, json.loads(src.read_text()))
            if merged != existing:
                dst.write_text(json.dumps(merged, indent=2) + "\n")
                log.append(f"merged hooks into {rel}")
            continue
        if dst.exists():
            log.append(f"kept existing {rel}")
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(src, dst)
        log.append(f"added {rel}")

    gitignore = target / ".gitignore"
    lines = gitignore.read_text().splitlines() if gitignore.exists() else []
    if IGNORED not in lines:
        gitignore.write_text("\n".join([*lines, IGNORED]) + "\n")
        log.append(f"ignored {IGNORED}")
    return log


def main() -> None:
    if len(sys.argv) != 2 or not Path(sys.argv[1]).is_dir():
        sys.exit("usage: uv run install.py <target-dir>")
    for line in install(Path(sys.argv[1]).resolve()):
        print(line)


if __name__ == "__main__":
    main()
