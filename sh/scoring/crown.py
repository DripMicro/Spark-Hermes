"""Who is crowned this round (the merge), as distinct from who is paid (the pooled window).

Payment is the pooled window's lower bound: it needs many instances and rewards consistency. The crown is a
different question — which strategy the repository should carry next — and it is answered on *this round's*
instances alone: among the sealed strategies, the one with the highest paired delta against the baseline on
these tasks (by credit: the share of withheld checks that hold), provided it actually beat the baseline here. Ties fall to the pooled Δc, then to the name, so the
verdict is total and recomputable from the published episodes.

A hotkey needs `min_paired` instances shared with the baseline to be a candidate; a round where nobody beat
the baseline crowns nobody.
"""

from __future__ import annotations

import hashlib

from sh.scoring.v2 import credit

BASELINE = "null"


def standings(episodes: list[dict], hotkeys: set[str], *, round_id: str) -> dict[str, dict]:
    """Per sealed hotkey: instances paired with the baseline this round, full passes, mean credit, and the paired
    delta of credit (the share of withheld checks that hold) against the baseline."""
    null: dict[str, float] = {}
    mine: dict[str, dict[str, float]] = {h: {} for h in hotkeys}
    full: dict[str, int] = {h: 0 for h in hotkeys}
    dq: dict[str, int] = {h: 0 for h in hotkeys}
    for e in episodes:
        if e.get("round_id") != round_id or e.get("void"):
            continue
        s, t = e.get("surface"), str(e.get("task_id"))
        if s == BASELINE:
            null[t] = credit(e)
        elif s in mine:
            mine[s][t] = credit(e)
            full[s] += bool(e.get("verified_success"))
            dq[s] += bool(e.get("disqualified"))
    out = {}
    for h in sorted(hotkeys):
        paired = [t for t in mine[h] if t in null]
        n = len(paired)
        delta = (sum(mine[h][t] for t in paired) - sum(null[t] for t in paired)) / n if n else None
        mean = sum(mine[h].values()) / len(mine[h]) if mine[h] else None
        out[h] = {
            "n": n,
            "verified": full[h],
            "dq": dq[h],
            "credit": None if mean is None else round(mean, 6),
            "delta": None if delta is None else round(delta, 6),
        }
    return out


def _tiebreak(round_id: str, hotkey: str) -> str:
    """A total order on tied strategies that a miner cannot grind toward: a hash of the round and the hotkey, not
    the hotkey itself (an ss58 that sorts first would win every tie). Recomputable by anyone."""
    return hashlib.sha256(f"{round_id}:{hotkey}".encode()).hexdigest()


def crown(
    episodes: list[dict],
    hotkeys: set[str],
    *,
    round_id: str,
    pooled_delta_c: dict[str, float],
    min_paired: int = 4,
    incumbent: str | None = None,
) -> dict:
    """The king of this round, with the standings that decided it. Among the eligible, a tie does not dethrone: the
    incumbent keeps the crown unless a challenger *strictly* beats it, and among challengers a tie falls to a hash
    of the round and the hotkey. A strategy disqualified on any of this round's instances cannot be crowned. A
    round where nobody is eligible crowns nobody; whether the incumbent then stays in `submissions/` is decided
    by `sh.validator.orchestrate.dethroned` (a challenger crowned over it, the pooled gate failing, or three
    rounds without the crown), not here."""
    st = standings(episodes, hotkeys, round_id=round_id)
    eligible = [
        h for h, s in st.items() if s["n"] >= min_paired and s["delta"] is not None and s["delta"] > 0 and not s["dq"]
    ]
    # the incumbent wins ties: sort it ahead of any challenger with the same delta (a lower rank key)
    ranked = sorted(
        eligible,
        key=lambda h: (-st[h]["delta"], -pooled_delta_c.get(h, 0.0), h != incumbent, _tiebreak(round_id, h)),
    )
    for i, h in enumerate(ranked, 1):
        st[h]["rank"] = i
    return {
        "schema": "sh-crown-v1",
        "round_id": round_id,
        "king": ranked[0] if ranked else None,
        "standings": st,
        "rule": f"highest paired delta vs baseline on this round's instances, > 0, ≥ {min_paired} paired, not "
        "disqualified; a tie does not dethrone the incumbent; other ties by pooled Δc then a round-keyed hash",
    }
