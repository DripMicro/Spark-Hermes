"""Who is crowned this round (the merge), as distinct from who is paid (the pooled window).

Payment is the pooled window's lower bound: it needs many instances and rewards consistency. The crown is a
different question — which strategy the repository should carry next — and it is answered on *this round's*
instances alone: among the sealed strategies, the one with the highest paired delta against the baseline on
these tasks, provided it actually beat the baseline here. Ties fall to the pooled Δc, then to the name, so the
verdict is total and recomputable from the published episodes.

A hotkey needs `min_paired` instances shared with the baseline to be a candidate; a round where nobody beat
the baseline crowns nobody.
"""

from __future__ import annotations

BASELINE = "null"


def standings(episodes: list[dict], hotkeys: set[str], *, round_id: str) -> dict[str, dict]:
    """Per sealed hotkey: instances paired with the baseline this round, verified count, and the paired delta."""
    null: dict[str, bool] = {}
    mine: dict[str, dict[str, bool]] = {h: {} for h in hotkeys}
    for e in episodes:
        if e.get("round_id") != round_id or e.get("void"):
            continue
        s, t, v = e.get("surface"), str(e.get("task_id")), bool(e.get("verified_success"))
        if s == BASELINE:
            null[t] = v
        elif s in mine:
            mine[s][t] = v
    out = {}
    for h in sorted(hotkeys):
        paired = [t for t in mine[h] if t in null]
        n = len(paired)
        delta = (sum(mine[h][t] for t in paired) - sum(null[t] for t in paired)) / n if n else None
        out[h] = {"n": n, "verified": sum(mine[h].values()), "delta": None if delta is None else round(delta, 6)}
    return out


def crown(
    episodes: list[dict], hotkeys: set[str], *, round_id: str, pooled_delta_c: dict[str, float], min_paired: int = 4
) -> dict:
    """The king of this round, with the standings that decided it."""
    st = standings(episodes, hotkeys, round_id=round_id)
    candidates = [h for h, s in st.items() if s["n"] >= min_paired and s["delta"] is not None and s["delta"] > 0]
    ranked = sorted(candidates, key=lambda h: (-st[h]["delta"], -pooled_delta_c.get(h, 0.0), h))
    for i, h in enumerate(ranked, 1):
        st[h]["rank"] = i
    return {
        "schema": "sh-crown-v1",
        "round_id": round_id,
        "king": ranked[0] if ranked else None,
        "standings": st,
        "rule": f"highest paired delta vs baseline on this round's instances, > 0, ≥ {min_paired} paired; "
        "ties by pooled Δc",
    }
