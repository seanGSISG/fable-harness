"""Tests for the two Jev gates: the route mapping and the done gate's decisions and I/O."""

import importlib.util
import io
import json
import subprocess
from pathlib import Path

import pytest

HOOKS = Path(__file__).parent.parent / "template" / ".claude" / "hooks"


def load(name: str):
    spec = importlib.util.spec_from_file_location(name, HOOKS / f"{name}.py")
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


route = load("jev_route")
done = load("jev_done")


@pytest.mark.parametrize("choice", ["lookup", "build", "hard", "big"])
def test_route_sure_answer_names_its_seat(choice):
    assert route.route(choice, 0.95) == f"ROUTE ({choice}, jev 0.95): {route.ROUTES[choice]}"


@pytest.mark.parametrize(("choice", "confidence"), [("build", 0.89), ("other", 0.99), ("nonsense", 1.0)])
def test_route_unsure_or_unknown_goes_to_advisor(choice, confidence):
    assert route.route(choice, confidence) == route.UNSURE


def test_route_without_key_fails_open(monkeypatch, capsys):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    monkeypatch.setattr("sys.stdin", io.StringIO(json.dumps({"prompt": "fix the bug"})))
    route.main()
    assert capsys.readouterr().out.startswith(route.UNSURE)


@pytest.mark.parametrize(
    ("rc", "noul", "action"),
    [
        (1, 0.99, "fix"),  # failing checks need no model
        (0, None, "review"),  # Jev unavailable
        (0, 0.9, "stop"),
        (0, 0.89, "review"),
        (0, 0.5, "review"),
        (0, 0.49, "continue"),
    ],
)
def test_decide(rc, noul, action):
    assert done.decide(rc, noul) == action


@pytest.fixture
def project(tmp_path, monkeypatch):
    """A project dir with the done gate's checks.sh; the hook reads stdin once."""
    (tmp_path / ".claude").mkdir()
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", str(tmp_path))
    monkeypatch.setattr("sys.stdin", io.StringIO("{}"))
    monkeypatch.chdir(tmp_path)
    return tmp_path


def write_checks(project: Path, body: str) -> None:
    (project / ".claude" / "checks.sh").write_text(body)


def test_done_gate_is_off_without_goal(project, capsys):
    done.main()
    assert capsys.readouterr().out == ""


def test_done_gate_blocks_on_failing_checks_and_counts(project, capsys):
    (project / "GOAL.md").write_text("# GOAL\ntests pass")
    write_checks(project, "echo 'FAILED test_x'; exit 1")
    done.main()
    out = json.loads(capsys.readouterr().out)
    assert out["decision"] == "block"
    assert "FAILED test_x" in out["reason"]
    assert (project / ".claude" / ".pushes").read_text() == "1"


def test_done_gate_brakes_at_push_cap(project, capsys):
    (project / "GOAL.md").write_text("# GOAL\ntests pass")
    (project / ".claude" / ".pushes").write_text(str(done.MAX_PUSHES))
    write_checks(project, "echo still failing; exit 1")
    done.main()
    assert "decision" not in json.loads(capsys.readouterr().out)
    assert "Stopped after 5 pushes" in (project / "REVIEW.md").read_text()
    assert not (project / ".claude" / ".pushes").exists()


def test_done_gate_flags_review_when_jev_is_down(project, capsys, monkeypatch):
    monkeypatch.delenv("TYPESAFE_API_KEY", raising=False)
    (project / "GOAL.md").write_text("# GOAL\ntests pass")
    write_checks(project, "echo all green")
    done.main()
    assert "REVIEW.md" in json.loads(capsys.readouterr().out)["systemMessage"]
    assert "all green" in (project / "REVIEW.md").read_text()


def test_template_checks_sh_fails_until_edited():
    checks = HOOKS.parent / "checks.sh"
    result = subprocess.run(["bash", str(checks)], capture_output=True, text=True)
    assert result.returncode == 1
    assert "still the template" in result.stdout
