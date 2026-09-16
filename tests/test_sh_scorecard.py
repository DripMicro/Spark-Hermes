"""The scorecard: what a miner is told, and why each part has to be there (FR-TRN)."""

from __future__ import annotations

from sh.cli.scorecard import render

CLOSE = {
    "round_id": "r1",
    "scores": {
        "5FA": {
            "hotkey": "5FA",
            "n": 12,
            "score": 0.13,
            "delta_c": 0.16,
            "mean_d": 0.30,
            "se": 0.11,
            "gate": True,
            "delta_e": {"api_calls": 0.2},
            "overfit_rate": 0.0,
            "dq": 0,
            "reason": None,
        },
        "5FB": {
            "hotkey": "5FB",
            "n": 3,
            "score": 0.0,
            "delta_c": 0.0,
            "mean_d": -0.1,
            "se": 0.2,
            "gate": False,
            "delta_e": {},
            "overfit_rate": 0.0,
            "dq": 0,
            "reason": "3 window episodes < 8",
        },
    },
    "weights": {"5FA": 1.0, "5FB": 0.0},
    "family_stats": {
        "process_lifecycle": {
            "null": {"n": 12, "successes": 4, "p": 0.33},
            "canon": {"p": 1.0, "delta_c": 0.67},
            "label": "frontier",
        }
    },
    "commitments_verified": {"t-1": True, "t-2": True},
}


def test_a_paid_miner_is_shown_the_arithmetic_that_paid_them():
    out = render(CLOSE, "5FA")
    assert "weight 1.0000" in out
    assert "+0.3000" in out and "0.1600" in out and "0.11" in out  # mean d, delta_c, se
    assert "passed" in out


def test_a_miner_paid_nothing_is_told_why():
    """A zero without a reason is unfalsifiable, which is the opposite of what the round is for."""
    out = render(CLOSE, "5FB")
    assert "scored nothing this round" in out
    assert "3 window episodes < 8" in out


def test_the_baseline_is_shown_because_that_is_what_the_score_means():
    out = render(CLOSE, "5FA")
    assert "process_lifecycle" in out and "frontier" in out
    assert "same instances" in out


def test_the_miner_is_given_what_they_need_to_check_the_grading():
    """The commitment scheme is worthless to a miner who is not shown how to verify it."""
    out = render(CLOSE, "5FA")
    assert "2 of 2 withheld commitments re-verified" in out and "all match" in out
    assert "hmac-sha256" in out and "sort_keys=True" in out


def test_a_commitment_mismatch_is_stated_plainly():
    bad = {**CLOSE, "commitments_verified": {"t-1": True, "t-2": False}}
    assert "MISMATCH — do not trust this round" in render(bad, "5FA")


def test_an_unknown_hotkey_gets_a_useful_answer_not_a_crash():
    out = render(CLOSE, "5FNobody")
    assert "No episodes for `5FNobody`" in out and "5FA" in out
