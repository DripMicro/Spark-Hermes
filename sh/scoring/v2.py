"""`sh-scoring-v3` — what a miner is paid for (spec §7).

A miner is paid for **beating the baseline on the same instances**, not for passing tasks. Since v3 an episode
counts by its **credit** — the share of the task's withheld checks that hold, 0 to 1 — rather than all or nothing:
on real multi-deliverable tasks the pinned model does a third of the work and nobody passes every check, so a
binary outcome measured nothing. Rounds scored before v3 carry no credit; theirs is 1 for a verified success. Everything here is a
pure function of archived Episode records and the family statistics computed from the reference arms, so
`sh scoring recompute` reproduces a validator's Score records byte for byte.

Three things carry most of the design:

  * **The reference rate is an estimate, not a constant.** Every episode of a family is compared against the same
    measured NULL rate, so that estimate's error does not average away with √n. It is added to the standard
    error explicitly, weighted by each family's share of the window. On the spec's worked example it is as large
    as the miner's own term.
  * **Efficiency is gated on correctness and never pays for cheaper failures.** It is measured only on verified
    successes, against the family's *measured* NULL median — never against `efficiency_reference`, which is an
    author's guess and would otherwise be a reward the author sets.
  * **The score is the measured gain; the lower bound is published as confidence.** `score` is the paired mean
    Δ of credit against the baseline over the window, after the overfit and copy penalties — signed, so a strategy
    below the baseline reads below zero. `weight` is a score's share among the strategies above the baseline.
    Δc, the one-sided 90 % lower bound of that mean, is published beside it as a statement of how sure the gain
    is; it was the score itself until 2026-09-18, and at six instances a round it read 0.000 for every miner,
    including each round's winner.
  * **Nothing is paid on thin evidence.** Below 8 window episodes a miner scores 0; below 4 NULL successes a
    family contributes no efficiency term.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass, field

__all__ = ["PARAMS_V2", "Params", "credit", "score", "stat", "weights"]


def credit(episode: dict) -> float:
    """An episode's credit: recorded since sh-episode-v3, else 1 for a verified success and 0 otherwise."""
    c = episode.get("credit")
    if isinstance(c, (int, float)) and not isinstance(c, bool):
        return max(0.0, min(1.0, float(c)))
    return 1.0 if episode.get("verified_success") else 0.0


@dataclass(frozen=True)
class Params:
    z: float = 1.28  # one-sided 90 %
    window: int = 8  # rounds
    min_episodes: int = 8  # fewer than this in the window pays nothing
    min_null_successes: int = 4  # fewer than this and the family's efficiency reference is not a measurement
    min_metric_samples: int = 4
    metrics: tuple[str, ...] = ("api_calls", "tool_calls")
    w_c: float = 1.0
    # The efficiency term is off (w_e = 0) from 2026-09-17: on the review's simulations it subtracted a negative
    # lower bound from honest improvers' pay and paid strategies slightly worse than the baseline for using fewer
    # calls, and calls are not what the token budget limits. Correctness (Δc) is the whole score until an
    # efficiency measure that compares paired, budget-aware token cost is designed.
    w_e: float = 0.0
    w_m: dict = field(default_factory=lambda: {"api_calls": 0.5, "tool_calls": 0.5})
    overfit_cutoff: float = 0.25
    copy_penalty: float = 0.5
    bootstrap: int = 200  # resamples for the NULL-median variance


PARAMS_V2 = Params()


@dataclass(frozen=True)
class FamilyReference:
    """What the NULL arm measured for one family over the window — the denominator a miner is judged against."""

    family: str
    n: int
    successes: int
    medians: dict  # metric -> median over NULL verified successes
    samples: dict  # metric -> the values behind that median, for the bootstrap
    requires_self_check: bool = False
    mean_credit: float | None = None  # the NULL arm's mean credit; None -> the binary success rate
    var_credit: float | None = None  # the variance of that credit; None -> p(1 - p)
    # The NULL arm's credit on each instance, task id -> credit. Every round runs the baseline on exactly the
    # instances the miners run, so the comparison can be made instance by instance instead of against the family
    # mean; that cancels how hard each instance happened to be, which is most of the spread. Empty -> unpaired.
    baseline: dict = field(default_factory=dict)

    @property
    def p(self) -> float:
        if self.mean_credit is not None:
            return self.mean_credit
        return self.successes / self.n if self.n else 0.0

    @property
    def var(self) -> float:
        # Floor the variance with the max-entropy variance for the measured credit rate, Laplace-smoothed on n. A
        # null arm that landed on a handful of identical credits (all 0, all 1, or a hand-tight cluster) has a
        # plug-in variance near 0, which would drop the reference-error term and make the baseline look certain from
        # a few samples; where the sample genuinely spreads, its own variance is larger and the floor is irrelevant.
        # a small floor, the max-entropy variance for the measured rate divided by n: it lifts an implausibly-zero
        # variance (all-identical null credits on few samples) off the floor without imposing worst-case spread on a
        # reference whose sample genuinely varies. Power at few tasks stays limited — that is a throughput question.
        p_tilde = (self.p * self.n + 1) / (self.n + 2) if self.n else 0.5
        floor = p_tilde * (1 - p_tilde) / self.n if self.n else p_tilde * (1 - p_tilde)
        raw = self.var_credit if self.var_credit is not None else self.p * (1 - self.p)
        return max(raw, floor)


def stat(episode: dict, reference: FamilyReference, params: Params = PARAMS_V2) -> tuple[float, dict, bool]:
    """One episode's contribution: `d` against the baseline, and log-ratios per efficiency metric. Returns
    `(d, ratios, paired)`.

    `d` is measured against the baseline's credit **on the same instance** when the window recorded one, and
    against the family's mean NULL credit otherwise. Pairing is what the board and the round pages have always
    said this number is, and it is free: the baseline runs on the same instances. It also removes the instance's
    own difficulty from the spread — on r0007 the baseline scored [0, 0, 0, 0, 1, 1], so unpaired differences
    carried that swing and the standard error was 40 % larger than the same episodes paired.

    The log ratio is symmetric in the sense that matters here — halving the calls and doubling them are equal and
    opposite — so a single outlier cannot dominate the mean the way a raw ratio would.
    """
    won = bool(episode.get("verified_success"))
    base = reference.baseline.get(str(episode.get("task_id")))
    paired = base is not None
    d = credit(episode) - (base if paired else reference.p)
    ratios: dict = {}
    if not won or reference.successes < params.min_null_successes:
        return d, ratios, paired
    for metric in params.metrics:
        ref = reference.medians.get(metric)
        got = episode.get(metric)
        if ref and isinstance(got, (int, float)) and got > 0:
            ratios[metric] = math.log(ref / got)
    # A family that asks for a self-check pays nothing for efficiency without one: spending fewer calls by
    # skipping the verification the task requires is not efficiency.
    if reference.requires_self_check and not episode.get("self_checked"):
        ratios = {m: 0.0 for m in ratios}
    return d, ratios, paired


def _median_variance(samples: list[float], resamples: int, rng: random.Random) -> float:
    """Bootstrap variance of a median. The NULL median is itself an estimate from a handful of episodes."""
    if len(samples) < 2:
        return 0.0
    medians = [statistics.median(rng.choices(samples, k=len(samples))) for _ in range(resamples)]
    return statistics.variance(medians) if len(set(medians)) > 1 else 0.0


@dataclass
class MinerWindow:
    """Everything about one hotkey over the scoring window."""

    hotkey: str
    episodes: list[dict] = field(default_factory=list)
    near_dup: bool = False
    prior_copy: float = 0.0

    @property
    def public_passers(self) -> int:
        """Episodes that did most of what the published half checks — the population overfitting is a share of."""

        def published(e: dict) -> float | None:
            f = e.get("published_fraction")
            if isinstance(f, (int, float)):
                return float(f)
            if "published_fraction" in e:  # recorded as None: the task publishes no half, so nothing was passed
                return None
            return 1.0 if e.get("published_pass") else 0.0

        return sum(1 for e in self.episodes if (f := published(e)) is not None and f >= 0.5)

    @property
    def overfit(self) -> int:
        return sum(1 for e in self.episodes if e.get("overfit"))

    @property
    def dq(self) -> int:
        return sum(1 for e in self.episodes if e.get("disqualified"))


def score(miner: MinerWindow, references: dict, params: Params = PARAMS_V2, *, seed: int = 0) -> dict:
    """The miner's weight contribution, with every term that produced it.

    Returns a record rather than a bare float so a validator's arithmetic can be audited without re-running it.
    """
    rng = random.Random(seed)
    eps = [e for e in miner.episodes if not e.get("void")]
    detail = {
        "hotkey": miner.hotkey,
        "n": len(eps),
        "score": 0.0,
        "delta_c": 0.0,
        "delta_e": {},
        "gate": False,
        "se": None,
        "overfit_rate": 0.0,
        "dq": miner.dq,
        "reason": None,
    }
    if len(eps) < params.min_episodes:
        detail["reason"] = f"{len(eps)} window episodes < {params.min_episodes}"
        return detail

    pairs = [(e, references[e["family"]]) for e in eps if e.get("family") in references]
    if not pairs:
        detail["reason"] = "no episode belongs to a family with reference statistics"
        return detail
    ds, rs, paired_flags = zip(*(stat(e, ref, params) for e, ref in pairs))
    n = len(ds)
    detail["paired"] = sum(paired_flags)

    # The family NULL rate is shared by every episode measured against it, so its error is not reduced by √n.
    # An episode paired against the baseline on its own instance never uses that shared estimate, so only the
    # unpaired remainder carries this term — and when every episode is paired it vanishes.
    ref_var = 0.0
    for family in {ref.family for _, ref in pairs}:
        ref = next(r for _, r in pairs if r.family == family)
        unpaired = sum(1 for (_, r), was in zip(pairs, paired_flags) if r.family == family and not was)
        if ref.n and unpaired:
            ref_var += (unpaired / n) ** 2 * ref.var / ref.n
    se = math.sqrt((statistics.variance(ds) / n if n > 1 else 0.0) + ref_var)
    mean_d = statistics.mean(ds)
    detail["se"] = round(se, 6)
    detail["mean_d"] = round(mean_d, 6)
    detail["delta_c"] = max(0.0, mean_d - params.z * se)
    detail["gate"] = mean_d + params.z * se >= 0.0

    if detail["gate"]:
        for metric in params.metrics:
            values = [r[metric] for r in rs if metric in r]
            if len(values) < params.min_metric_samples:
                continue
            ref_median_var = 0.0
            for family in {ref.family for _, ref in pairs}:
                ref = next(r for _, r in pairs if r.family == family)
                share = sum(1 for _, r in pairs if r.family == family) / n
                samples = [float(v) for v in ref.samples.get(metric, [])]
                median = ref.medians.get(metric)
                if samples and median:
                    # variance of log(median) ≈ var(median) / median²
                    ref_median_var += share**2 * _median_variance(samples, params.bootstrap, rng) / (median**2)
            se_m = math.sqrt((statistics.variance(values) / len(values) if len(values) > 1 else 0.0) + ref_median_var)
            detail["delta_e"][metric] = max(-1.0, min(1.0, statistics.mean(values) - params.z * se_m))

    raw = params.w_c * mean_d + params.w_e * sum(params.w_m.get(m, 0.0) * x for m, x in detail["delta_e"].items())

    ofr = miner.overfit / max(1, miner.public_passers)
    detail["overfit_rate"] = round(ofr, 4)
    if miner.public_passers >= params.min_episodes and ofr > params.overfit_cutoff:
        detail["reason"] = f"overfit rate {ofr:.2f} > {params.overfit_cutoff}"
        return detail
    if miner.dq >= 2:
        detail["reason"] = f"{miner.dq} disqualified episodes"
        return detail
    if miner.near_dup:
        detail["reason"] = "bundle is a near-duplicate"
        return detail

    detail["score"] = round(raw * (1 - ofr) ** 2 * (1 - params.copy_penalty * miner.prior_copy), 6)
    if detail["score"] <= 0.0:  # a score that earns no weight always says why
        detail["reason"] = f"at or below the baseline: Δ {mean_d:+.3f} ± {se:.3f}"
    return detail


def weights(scores: dict) -> dict:
    """Normalise to a weight vector. NULL and CANON are never in `scores` — they are references, not competitors."""
    total = sum(max(0.0, v) for v in scores.values())
    if total <= 0:
        return {h: 0.0 for h in scores}
    return {h: max(0.0, v) / total for h, v in scores.items()}
