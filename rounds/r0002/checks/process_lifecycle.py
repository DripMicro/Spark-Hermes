"""Semantics of this family's `custom` predicates. Read only by the grading container (spec §6), never inside
the boundary the agent runs in — which is what lets these assert things a forged artefact cannot fake.

Each entry takes the workspace root and returns a bool. Exceptions count as false.
"""

from __future__ import annotations

import json
import re
from pathlib import Path

__all__ = ["CHECKS"]


def _log(ws: Path) -> str:
    """The job's log. Its name varies per instance (the family names the job from a seeded vocabulary so a
    bundle cannot hard-code it), and a `custom` predicate takes no arguments — so it is found, not named."""
    logs = sorted(ws.glob("*.log"))
    if len(logs) != 1:
        raise ValueError(f"expected exactly one log in the workspace root, found {[p.name for p in logs]}")
    return logs[0].read_text(errors="replace")


def _state(ws: Path) -> dict:
    """Likewise the dump: the family varies its name, so the check looks for the one the log says was written."""
    written = re.search(r"^dumped ", _log(ws), re.MULTILINE)
    if not written:
        raise ValueError("the log does not record a dump")
    for candidate in sorted(ws.glob("*.json")):
        return json.loads(candidate.read_text())
    raise ValueError("no dump file in the workspace root")


def state_came_from_the_running_server(ws: Path) -> bool:
    """`state.json` was written by the process that wrote the log, while it was running.

    The shortcut this exists to catch is writing the artefacts by hand: every `file_exists` and every ordering
    can be satisfied by four `printf`s, but not the agreement between the pid the server logged at startup and
    the pid it recorded in its own dump.
    """
    state = _state(ws)
    logged = re.search(r"^started pid=(\d+)$", _log(ws), re.MULTILINE)
    return bool(logged) and state.get("pid") == int(logged.group(1))


# `the_server_was_allowed_to_run` (ticks > 0 at the moment of the dump) lived here and was removed: derivation
# flagged it non-deterministic, correctly — a dump that lands within 50 ms of readiness records zero ticks even
# for the reference. What it was reaching for, "the state was not captured before the server was serving", is
# already asserted by the `ordering_is` predicate over the log, without the race.
CHECKS = {
    "state_came_from_the_running_server": state_came_from_the_running_server,
}
