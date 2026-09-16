"""What a round does to the PRs it sealed: merge the king, close the rest, touch nothing else."""

from __future__ import annotations

from sh.validator.orchestrate import outcome


def _seal(**active):
    return {
        "active": {h: {"pr": pr, "incumbent": pr is None} for h, pr in active.items()},
        "rejected": {},
    }


def test_the_king_is_merged_and_every_other_challenger_is_closed():
    sealed = _seal(A=101, B=102, C=103)
    plan = outcome(sealed, "B")
    assert plan == {"king": "B", "merge": 102, "close": [101, 103]}


def test_no_king_closes_every_challenger():
    """A round nobody won crowns no one — but the losing PRs still close with the round."""
    plan = outcome(_seal(A=101, B=102), None)
    assert plan["king"] is None and plan["merge"] is None and plan["close"] == [101, 102]


def test_an_incumbent_king_has_no_pr_to_merge():
    """A crowned strategy already lives in submissions/; keeping the crown merges nothing."""
    plan = outcome(_seal(KING=None, A=101), "KING")
    assert plan["king"] == "KING" and plan["merge"] is None and plan["close"] == [101]


def test_a_challenger_that_dethrones_the_incumbent_is_merged():
    plan = outcome(_seal(KING=None, A=101), "A")
    assert plan["king"] == "A" and plan["merge"] == 101 and plan["close"] == []


def test_prs_rejected_at_seal_are_closed_too():
    sealed = _seal(A=101)
    sealed["rejected"] = {"104": "L4 SOUL.md: inline shell marker"}
    assert outcome(sealed, "A")["close"] == [104]


def test_prs_the_seal_never_named_are_never_touched():
    """A dependabot or maintenance PR is not in the seal, so it cannot appear in the plan at all."""
    plan = outcome(_seal(A=101, B=102), "A")
    assert 85 not in plan["close"] and plan["merge"] != 85


def test_a_king_outside_the_seal_is_a_bug_not_a_verdict():
    """The crown rule only ranks sealed strategies; anything else reaching outcome() is a programming error."""
    import pytest

    with pytest.raises(ValueError):
        outcome(_seal(A=101), "GHOST")


def test_a_pull_request_is_a_strategy_by_what_it_touches_not_by_its_label():
    """A miner cannot label a PR, and a maintenance PR must never be swept into a round."""
    from sh.validator.orchestrate import pr_role

    assert pr_role([]) == "maintenance"
    assert pr_role(["5Fa"]) == "strategy"
    assert pr_role(["5Fa", "5Fb"]) == "malformed"


def test_the_newest_pr_per_hotkey_counts_and_the_rest_are_superseded():
    from sh.validator.orchestrate import one_per_hotkey

    keep, superseded = one_per_hotkey(
        [{"number": 7, "changed": ["A"]}, {"number": 9, "changed": ["B"]}, {"number": 12, "changed": ["A"]}]
    )
    assert keep["A"]["number"] == 12 and keep["B"]["number"] == 9
    assert superseded == {7: "superseded by #12 (one PR per hotkey per round)"}
