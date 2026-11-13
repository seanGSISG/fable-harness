"""Tests for install.py: it never overwrites, merges hooks once, and is safe to re-run."""

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
import install  # noqa: E402


def test_fresh_install_copies_template_and_ignores_counter(tmp_path):
    install.install(tmp_path)
    assert (tmp_path / ".claude" / "agents" / "advisor.md").exists()
    assert (tmp_path / ".claude" / "hooks" / "jev_done.py").exists()
    assert (tmp_path / "receipts" / ".gitkeep").exists()
    assert not (tmp_path / "GOAL.md").exists()  # the done gate stays off until a run starts
    assert not list(tmp_path.rglob("__pycache__"))  # test runs leave bytecode in template/
    assert ".claude/.pushes" in (tmp_path / ".gitignore").read_text().splitlines()


def test_existing_files_are_kept(tmp_path):
    (tmp_path / "STATE.md").write_text("mine")
    install.install(tmp_path)
    assert (tmp_path / "STATE.md").read_text() == "mine"


def test_existing_settings_gain_hooks_once(tmp_path):
    settings = tmp_path / ".claude" / "settings.json"
    settings.parent.mkdir()
    own_hook = {"hooks": [{"type": "command", "command": "echo mine"}]}
    settings.write_text(json.dumps({"model": "opus", "hooks": {"Stop": [own_hook]}}))

    install.install(tmp_path)
    install.install(tmp_path)  # re-run must not duplicate

    merged = json.loads(settings.read_text())
    assert merged["model"] == "opus"
    assert merged["hooks"]["Stop"][0] == own_hook
    assert len(merged["hooks"]["Stop"]) == 2
    assert len(merged["hooks"]["UserPromptSubmit"]) == 1
