"""What a miner is paid for. Each test pins one rule the scorer exists to enforce."""

from __future__ import annotations

import statistics

from sh.scoring.v2 import FamilyReference, MinerWindow, score, stat, weights

REF = FamilyReference(
    family="f",
    n=16,
    successes=8,
    medians={"api_calls": 10, "tool_calls": 10},
    samples={"api_calls": [9, 10, 10, 11, 12, 8, 10, 10], "tool_calls": [9, 10, 10, 11, 12, 8, 10, 10]},
)


def _eps(n, wins, *, calls=10, family="f", **extra):
    return [
        {
            "family": family,
            "verified_success": i < wins,
            "published_pass": i < wins,
            "api_calls": calls,
            "tool_calls": calls,
            "self_checked": True,
            "overfit": False,
            "disqualified": False,
            **extra,
        }
        for i in range(n)
    ]


def test_a_miner_at_the_baseline_rate_is_paid_nothing():
    """The whole design: passing tasks is not the achievement, beating the reference is."""
    s = score(MinerWindow("m", _eps(16, 8)), {"f": REF})
    assert s["score"] == 0.0 and s["delta_c"] == 0.0


def test_a_miner_clearly_above_the_baseline_is_paid():
    s = score(MinerWindow("m", _eps(16, 15)), {"f": REF})
    assert s["score"] > 0 and s["delta_c"] > 0 and s["gate"]


def test_a_thin_window_pays_nothing_however_good_it_looks():
    s = score(MinerWindow("m", _eps(4, 4)), {"f": REF})
    assert s["score"] == 0.0 and "window episodes" in s["reason"]


def test_the_reference_error_is_carried_into_the_standard_error():
    """The spec's central statistical point: the family rate is shared by every episode, so its error does not
    average away. A reference measured on few episodes must pay less than the same result on many."""
    thin = FamilyReference(family="f", n=8, successes=4, medians=REF.medians, samples=REF.samples)
    fat = FamilyReference(family="f", n=200, successes=100, medians=REF.medians, samples=REF.samples)
    on_thin = score(MinerWindow("m", _eps(16, 14)), {"f": thin})
    on_fat = score(MinerWindow("m", _eps(16, 14)), {"f": fat})
    assert on_thin["se"] > on_fat["se"]
    assert on_thin["delta_c"] < on_fat["delta_c"]


def test_efficiency_needs_the_correctness_gate():
    """Spending fewer calls while failing more often is not efficiency."""
    losing = score(MinerWindow("m", _eps(16, 1, calls=2)), {"f": REF})
    assert not losing["gate"] and losing["delta_e"] == {}


def test_efficiency_is_measured_against_a_measurement_not_an_author_s_guess():
    """With fewer than 4 NULL successes the family's median is not a measurement, so no efficiency is paid."""
    unmeasured = FamilyReference(family="f", n=16, successes=2, medians={"api_calls": 10}, samples={})
    d, ratios, _ = stat({"family": "f", "verified_success": True, "api_calls": 5}, unmeasured)
    assert ratios == {}


def test_skipping_a_required_self_check_earns_no_efficiency():
    """The cheapest way to spend fewer calls is to skip the verification the family asks for."""
    checking = FamilyReference(**{**REF.__dict__, "requires_self_check": True})
    _, with_check, _ = stat({"family": "f", "verified_success": True, "api_calls": 5, "self_checked": True}, checking)
    _, without, _ = stat({"family": "f", "verified_success": True, "api_calls": 5, "self_checked": False}, checking)
    assert with_check["api_calls"] > 0
    assert without["api_calls"] == 0.0


def test_an_overfitting_miner_is_zeroed():
    eps = _eps(16, 16)
    for e in eps[:8]:
        e["overfit"] = True
    s = score(MinerWindow("m", eps), {"f": REF})
    assert s["score"] == 0.0 and "overfit rate" in s["reason"]


def test_two_disqualifications_zero_a_miner():
    eps = _eps(16, 16)
    eps[0]["disqualified"] = eps[1]["disqualified"] = True
    s = score(MinerWindow("m", eps), {"f": REF})
    assert s["score"] == 0.0 and "disqualified" in s["reason"]


def test_a_near_duplicate_bundle_is_zeroed():
    s = score(MinerWindow("m", _eps(16, 15), near_dup=True), {"f": REF})
    assert s["score"] == 0.0 and "near-duplicate" in s["reason"]


def test_void_episodes_are_not_evidence():
    """A provider outage must neither help nor hurt."""
    eps = _eps(16, 15) + _eps(4, 0, void=True)
    s = score(MinerWindow("m", eps), {"f": REF})
    assert s["n"] == 16


def test_scoring_is_reproducible():
    """`sh scoring recompute` has to reproduce a validator's record byte for byte."""
    a = score(MinerWindow("m", _eps(16, 14, calls=6)), {"f": REF}, seed=7)
    b = score(MinerWindow("m", _eps(16, 14, calls=6)), {"f": REF}, seed=7)
    assert a == b


def test_weights_normalise_and_ignore_the_references():
    w = weights({"a": 0.3, "b": 0.1, "c": 0.0})
    assert abs(sum(w.values()) - 1.0) < 1e-9 and w["c"] == 0.0
    assert weights({"a": 0.0, "b": 0.0}) == {"a": 0.0, "b": 0.0}  # an all-zero round pays no one


def test_the_worked_example_from_the_spec_reproduces():
    """+0.25 over a NULL rate of 0.4, 64 episodes across 4 families with 16 NULL episodes each."""
    refs, eps = {}, []
    for i in range(4):
        fam = f"f{i}"
        refs[fam] = FamilyReference(family=fam, n=16, successes=6, medians={}, samples={})
        eps += _eps(16, 10, family=fam)  # 10/16 = 0.625 vs 0.375 → d ≈ +0.25
    s = score(MinerWindow("m", eps), refs)
    assert 0.2 < s["mean_d"] < 0.3
    assert 0.05 < s["se"] < 0.12  # the spec's 0.083, to the nearest band
    assert 0.10 < s["delta_c"] < 0.20  # the spec's 0.144


def test_credit_is_scored_against_the_baseline_s_mean_credit():
    """sh-scoring-v3: nobody passes every check; doing more of the work than the baseline, consistently, pays."""
    from sh.scoring.v2 import FamilyReference, MinerWindow, credit, score

    null = [0.40, 0.35, 0.45, 0.40, 0.38, 0.42, 0.40, 0.40]
    ref = FamilyReference(
        "f", n=8, successes=0, medians={}, samples={}, mean_credit=sum(null) / 8, var_credit=statistics.pvariance(null)
    )
    good = MinerWindow(
        "A",
        [
            {"family": "f", "task_id": f"t{i}", "credit": 0.75 + 0.01 * (i % 3), "verified_success": False}
            for i in range(16)
        ],
    )
    flat = MinerWindow(
        "B", [{"family": "f", "task_id": f"t{i}", "credit": 0.40, "verified_success": False} for i in range(16)]
    )
    s_good, s_flat = score(good, {"f": ref}), score(flat, {"f": ref})
    # the reference-variance floor makes 8 tightly-clustered null samples less than certain, so Δc is conservative
    assert s_good["delta_c"] > 0.25 and s_good["score"] == s_good["delta_c"]  # efficiency is off: score is Δc alone
    assert s_flat["delta_c"] == 0.0 and s_flat["score"] == 0.0
    assert credit({"verified_success": True}) == 1.0 and credit({"credit": 0.25, "verified_success": True}) == 0.25


def test_a_task_with_no_published_half_is_not_a_public_passer():
    """swe_fix publishes nothing, so nothing was passed: such episodes must not pad the overfit denominator."""
    from sh.scoring.v2 import MinerWindow

    w = MinerWindow("hk")
    w.episodes = [
        {"published_fraction": None, "published_pass": True},  # sh-episode-v3, empty published half
        {"published_fraction": 0.75},
        {"published_pass": True},  # pre-v3 record: the verdict stands
        {"published_fraction": 0.25},
    ]
    assert w.public_passers == 2


def test_a_delta_is_measured_against_the_baseline_on_the_same_instance():
    """The board and the round pages have always called this 'per instance'. Pairing is free — the baseline runs
    on the instances the miners run — and it removes the instance's own difficulty from the spread, which is most
    of it: on r0007 the baseline scored [0, 0, 0, 0, 1, 1]."""
    import statistics

    from sh.scoring.v2 import FamilyReference, stat

    hard, easy = "t-hard", "t-easy"
    ref = FamilyReference(
        family="f", n=2, successes=1, medians={}, samples={}, mean_credit=0.5, var_credit=0.25,
        baseline={hard: 0.0, easy: 1.0},
    )  # fmt: skip
    # a miner that is exactly the baseline everywhere: zero delta and, paired, zero spread
    same = [stat({"family": "f", "task_id": t, "credit": c}, ref)[0] for t, c in ((hard, 0.0), (easy, 1.0))]
    assert same == [0.0, 0.0]
    # unpaired, the same episodes look like ±0.5 — the instance's difficulty, not the miner's doing
    blind = FamilyReference(**{**ref.__dict__, "baseline": {}})
    assert [stat({"family": "f", "task_id": t, "credit": c}, blind)[0] for t, c in ((hard, 0.0), (easy, 1.0))] == [
        -0.5,
        0.5,
    ]
    assert statistics.pstdev(same) < statistics.pstdev(
        [stat({"family": "f", "task_id": t, "credit": c}, blind)[0] for t, c in ((hard, 0.0), (easy, 1.0))]
    )
    # a miner that beats the baseline on the hard instance is credited for exactly that
    assert stat({"family": "f", "task_id": hard, "credit": 0.75}, ref)[0] == 0.75
    assert stat({"family": "f", "task_id": hard, "credit": 0.75}, ref)[2] is True
    # an instance the window has no baseline for falls back to the family mean, and says so
    d, _, paired = stat({"family": "f", "task_id": "t-unseen", "credit": 0.5}, ref)
    assert d == 0.0 and paired is False


def test_the_shared_baseline_error_is_charged_only_to_unpaired_episodes():
    """That term exists because every unpaired episode leans on one estimate of the NULL rate. A paired episode
    never touches it, so with everything paired the term is gone and the standard error is the miner's own."""
    from sh.scoring.v2 import FamilyReference, MinerWindow, score

    tasks = {f"t{i}": float(i % 2) for i in range(10)}
    ref = FamilyReference(
        family="f", n=10, successes=5, medians={}, samples={}, mean_credit=0.5, var_credit=0.25, baseline=tasks
    )
    eps = [{"family": "f", "task_id": t, "credit": c, "round_id": "r1"} for t, c in tasks.items()]
    paid = score(MinerWindow("5F", eps), {"f": ref})
    assert paid["paired"] == 10
    blind = score(MinerWindow("5F", eps), {"f": FamilyReference(**{**ref.__dict__, "baseline": {}})})
    assert blind["paired"] == 0
    assert paid["se"] < blind["se"]  # the same episodes, without the instance difficulty and the shared estimate
