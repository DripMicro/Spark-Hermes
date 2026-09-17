"""The crown is this round's verdict; payment is the window's. They must not be confused."""

from __future__ import annotations

from sh.scoring.crown import crown, standings


def _ep(surface, task, ok, round_id="r0002", **kw):
    return {"surface": surface, "task_id": task, "verified_success": ok, "round_id": round_id, **kw}


def _round(null: str, miners: dict[str, str], round_id="r0002"):
    eps = [_ep("null", f"t{i}", c == "1", round_id) for i, c in enumerate(null)]
    for h, pattern in miners.items():
        eps += [_ep(h, f"t{i}", c == "1", round_id) for i, c in enumerate(pattern)]
    return eps


def test_the_best_paired_delta_this_round_is_king():
    eps = _round("11110000", {"A": "11111100", "B": "11111000", "C": "11110000"})
    c = crown(eps, {"A", "B", "C"}, round_id="r0002", pooled_delta_c={})
    assert c["king"] == "A"
    assert c["standings"]["A"]["delta"] == 0.25 and c["standings"]["A"]["rank"] == 1
    assert c["standings"]["B"]["rank"] == 2 and "rank" not in c["standings"]["C"]


def test_nobody_is_crowned_when_nobody_beat_the_baseline():
    eps = _round("11110000", {"A": "11110000", "B": "11100000"})
    assert crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={"A": 0.5})["king"] is None


def test_ties_fall_to_the_pooled_lower_bound_then_a_hash_and_the_incumbent_keeps_the_crown():
    eps = _round("11110000", {"A": "11111000", "B": "11111000"})
    assert crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={"A": 0.0, "B": 0.1})["king"] == "B"
    # no pooled edge: a round-keyed hash decides, not the name (so a low-sorting ss58 cannot grind ties)
    import hashlib

    hashed = min(("A", "B"), key=lambda h: hashlib.sha256(f"r0002:{h}".encode()).hexdigest())
    assert crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={})["king"] == hashed
    # a tie does not dethrone: the incumbent keeps the crown over an equal challenger
    assert crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={}, incumbent="A")["king"] == "A"
    assert crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={}, incumbent="B")["king"] == "B"


def test_a_strategy_disqualified_this_round_cannot_be_crowned():
    eps = _round("00000000", {"A": "11111111"})
    eps.append(_ep("A", "t0", True, disqualified=True))  # tampered on one instance
    assert crown(eps, {"A"}, round_id="r0002", pooled_delta_c={})["king"] is None


def test_only_this_rounds_instances_count_and_void_episodes_do_not():
    eps = _round("11110000", {"A": "11110000"}) + _round("00000000", {"A": "11111111"}, round_id="r0001")
    eps.append(_ep("A", "t7", True, void=True))  # a provider outage is not a pass
    st = standings(eps, {"A"}, round_id="r0002")
    assert st["A"] == {"n": 8, "verified": 4, "dq": 0, "credit": 0.5, "delta": 0.0}


def test_a_hotkey_with_too_few_paired_instances_is_not_a_candidate():
    eps = _round("1100", {"A": "1110"})  # 4 instances, delta +0.25
    assert crown(eps, {"A"}, round_id="r0002", pooled_delta_c={}, min_paired=5)["king"] is None
    assert crown(eps, {"A"}, round_id="r0002", pooled_delta_c={}, min_paired=4)["king"] == "A"


def test_the_crown_counts_the_share_of_checks_not_only_full_passes():
    """Nobody passes every check of a large task; the one that does more of the work than the baseline is king."""
    eps = [_ep("null", f"t{i}", False, credit=0.40) for i in range(8)]
    eps += [_ep("A", f"t{i}", False, credit=0.55) for i in range(8)]
    eps += [_ep("B", f"t{i}", False, credit=0.35) for i in range(8)]
    c = crown(eps, {"A", "B"}, round_id="r0002", pooled_delta_c={})
    assert c["king"] == "A" and c["standings"]["A"]["delta"] == 0.15 and c["standings"]["A"]["verified"] == 0
    assert "rank" not in c["standings"]["B"]
