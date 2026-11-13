#!/usr/bin/env bash
# Prints evidence for every condition in GOAL.md, then exits non-zero if any check failed.
# The done gate (.claude/hooks/jev_done.py) runs this each time Claude tries to stop while
# GOAL.md exists. Jev reads this output, not Claude's summary, so print real command output.
#
# Use: add one `check <command>` line per "Done means" condition in GOAL.md.
set -u
cd "$(dirname "$0")/.."
fail=0

# check <command...>: prints the command, the last 40 lines of its output and its exit code.
check() {
  echo "\$ $*"
  "$@" 2>&1 | tail -n 40
  local rc=${PIPESTATUS[0]}
  echo "exit $rc"
  echo
  [ "$rc" -eq 0 ] || fail=1
}

# Examples that match .claude/GOAL.template.md. Replace them with your own checks:
# check npm test
# check ./scripts/bench.sh
# check ls receipts/

echo "checks.sh is still the template: add one check per condition in GOAL.md"
fail=1

exit "$fail"
