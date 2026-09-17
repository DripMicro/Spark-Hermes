"""The miner CLI's fork-resubmit path: a fork's open PR is found by branch and owner, not by `owner:branch`."""

from __future__ import annotations

import json

import sh.cli.miner as miner


def test_an_open_fork_pr_is_found_by_branch_and_owner(monkeypatch):
    calls = []

    def fake_run(cmd, cwd=None, check_rc=True):
        calls.append(cmd)
        if cmd[:3] == ["gh", "pr", "list"]:
            return json.dumps(
                [
                    {"number": 41, "headRepositoryOwner": {"login": "someone-else"}},
                    {"number": 42, "headRepositoryOwner": {"login": "alice"}},
                ]
            )
        return ""

    monkeypatch.setattr(miner, "_run", fake_run)
    assert miner._open_pr_for("org/repo", "main", "miner/5HK", "alice") == 42
    assert miner._open_pr_for("org/repo", "main", "miner/5HK", "nobody") is None
    assert miner._open_pr_for("org/repo", "main", "miner/5HK") == 41  # no owner filter: the first open PR
    assert all("alice:miner/5HK" not in " ".join(c) for c in calls)  # never the owner:branch form gh returns empty for
