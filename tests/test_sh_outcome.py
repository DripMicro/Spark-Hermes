"""What a round does to the PRs it sealed: merge the king, close the rest, touch nothing else."""

from __future__ import annotations

from sh.validator.orchestrate import outcome


def _seal(**active):
    return {
        "active": {h: {"pr": pr, "incumbent": pr is None} for h, pr in active.items()},
        "rejected": {},
    }


def test_the_top_weight_is_merged_and_every_other_challenger_is_closed():
    sealed = _seal(A=101, B=102, C=103)
    plan = outcome(sealed, {"A": 0.2, "B": 0.7, "C": 0.1})
    assert plan == {"king": "B", "merge": 102, "close": [101, 103]}


def test_no_king_when_nobody_beat_the_baseline():
    """All-zero weights pay no one and crown no one — but the losing PRs still close with the round."""
    plan = outcome(_seal(A=101, B=102), {"A": 0.0, "B": 0.0})
    assert plan["king"] is None and plan["merge"] is None and plan["close"] == [101, 102]


def test_an_incumbent_king_has_no_pr_to_merge():
    """A crowned strategy already lives in submissions/; keeping the crown merges nothing."""
    plan = outcome(_seal(KING=None, A=101), {"KING": 0.6, "A": 0.4})
    assert plan["king"] == "KING" and plan["merge"] is None and plan["close"] == [101]


def test_a_challenger_that_dethrones_the_incumbent_is_merged():
    plan = outcome(_seal(KING=None, A=101), {"KING": 0.3, "A": 0.7})
    assert plan["king"] == "A" and plan["merge"] == 101 and plan["close"] == []


def test_prs_rejected_at_seal_are_closed_too():
    sealed = _seal(A=101)
    sealed["rejected"] = {"104": "L4 SOUL.md: inline shell marker"}
    plan = outcome(sealed, {"A": 1.0})
    assert plan["close"] == [104]


def test_prs_the_seal_never_named_are_never_touched():
    """A dependabot or maintenance PR is not in the seal, so it cannot appear in the plan at all."""
    plan = outcome(_seal(A=101, B=102), {"A": 1.0, "B": 0.0})
    assert 85 not in plan["close"] and plan["merge"] != 85
