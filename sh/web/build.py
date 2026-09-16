"""A closed round's page (spec §10) — static, built from `close.json`, served from `docs/rounds/<id>/`.

It is generated from published artefacts alone, which is the point: everything a miner sees here is something they
can recompute. A page that knows something its readers cannot check is a page they have to trust.

    python -m sh.web.build --close DIR/close.json --out docs/rounds/<id>/
"""

from __future__ import annotations

import argparse
import html
import json
import sys
import time
from pathlib import Path

DEFAULT_REPO = "gittensor-model-hub/Spark-Hermes"
DEFAULT_BRANCH = "sh/v2-pipeline"


def _e(x) -> str:
    return html.escape(str(x))


def _pct(p) -> str:
    return "—" if p is None else f"{100 * p:.0f}%"


def _signed(x, digits: int = 3) -> str:
    return "—" if x is None else f"{x:+.{digits}f}"


def _cls(x) -> str:
    return "zero" if not x else ("pos" if x > 0 else "neg")


def render(close: dict, meta: dict | None = None) -> str:
    """The page for one closed round. `meta` is the round's entry in `rounds/index.json` (king, export sizes,
    dataset URL) plus `repo`/`branch` for artefact links; the page degrades to `close.json` alone without it."""
    meta = meta or {}
    rid = str(close.get("round_id", ""))
    repo, branch = meta.get("repo", DEFAULT_REPO), meta.get("branch", DEFAULT_BRANCH)
    weights = close.get("weights", {})
    king = meta.get("king") or (
        max(weights, key=lambda h: weights[h]) if weights and max(weights.values()) > 0 else None
    )
    tree = f"https://github.com/{repo}/tree/{branch}/rounds/{rid}"
    blob = f"https://github.com/{repo}/blob/{branch}/rounds/{rid}"

    rows = sorted(close.get("scores", {}).values(), key=lambda s: (-weights.get(s["hotkey"], 0.0), -s.get("score", 0)))
    body = []
    for rank, s in enumerate(rows, 1):
        h, w = s["hotkey"], weights.get(s["hotkey"], 0.0)
        crown = ' <span class="crown" title="crowned">👑</span>' if h == king else ""
        why = f'<span class="why">{_e(s["reason"])}</span>' if w == 0 and s.get("reason") else ""
        body.append(
            f'<tr><td class="l"><span class="hk">{_e(h)}</span>{crown}{why}</td><td>{rank}</td><td>{s["n"]}</td>'
            f'<td class="{_cls(s.get("mean_d"))}">{_signed(s.get("mean_d"))}</td><td>{s.get("delta_c", 0):.3f}</td>'
            f"<td>{'yes' if s.get('gate') else 'no'}</td><td>{s.get('overfit_rate', 0):.2f}</td><td>{s.get('dq', 0)}</td>"
            f'<td>{s.get("score", 0):.4f}</td><td class="{"" if w else "zero"}">{w:.3f}</td></tr>'
        )
    families = "".join(
        f'<tr><td class="l">{_e(f)}</td><td>{r["null"]["n"]}</td><td>{_pct(r["null"]["p"])}</td>'
        f'<td>{_pct(r["canon"]["p"])}</td><td>{_signed(r["canon"].get("delta_c"))}</td><td class="l">{_e(r.get("label"))}</td></tr>'
        for f, r in close.get("family_stats", {}).items()
    )

    verified = close.get("commitments_verified", {})
    checked = sum(1 for v in verified.values() if v is not None)
    ok = close.get("commitments_ok")
    closed_at = meta.get("closed_at")
    when = time.strftime("%Y-%m-%d %H:%M UTC", time.gmtime(closed_at)) if closed_at else ""
    hf = meta.get("hf")
    stats = [
        (str(close.get("episodes", 0)), "episodes"),
        (str(len(close.get("tasks", []))), "instances"),
        (f'<span class="crown">👑</span> {_e(king)}' if king else '<span class="zero">none</span>', "king"),
        ("—" if meta.get("sft_rows") is None else str(meta["sft_rows"]), "SFT rows"),
        ("—" if meta.get("dpo_pairs") is None else str(meta["dpo_pairs"]), "DPO pairs"),
        (
            f'<span class="{"pos" if ok else "neg"}">{checked}/{len(verified)} {"match" if ok else "MISMATCH"}</span>',
            "commitments",
        ),
    ]
    strip = "".join(f"<div class='stat'><b>{v}</b><span>{k}</span></div>" for v, k in stats)
    links = [
        (f"{blob}/close.json", "close.json"),
        (f"{blob}/reveal.json", "reveal.json"),
        (f"{tree}/scorecards", "scorecards"),
        (f"{tree}/checks", "checks"),
        (f"{blob}/manifest.json", "manifest.json"),
    ] + ([(hf, "dataset")] if hf else [])
    artefacts = " · ".join(f'<a href="{_e(u)}">{_e(t)}</a>' for u, t in links)

    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Spark-Hermes {_e(rid)}</title>
<meta name="description" content="Scores, weights and verification for round {_e(rid)} of the Spark-Hermes strategy competition.">
<link rel="stylesheet" href="../../site.css">
</head>
<body>
<nav class="nav">
  <a class="brand" href="../../">Spark-Hermes</a>
  <a href="../../live/">Live</a>
  <a href="../../live/#rounds" aria-current="page">Rounds</a>
  <a href="https://github.com/{_e(repo)}/blob/{_e(branch)}/submissions/README.md">Submit</a>
  <a href="https://github.com/{_e(repo)}">GitHub</a>
</nav>
<main>
  <div class="head"><h1>Round {_e(rid)}</h1><span class="muted small">closed {_e(when) if when else "—"} · era {_e(close.get("era", ""))} · {_e(close.get("schema", ""))}</span></div>
  <div class="strip">{strip}</div>
  <section class="panel">
    <h2>Scores <small>Δc, the one-sided 90% lower bound of Δ vs baseline, is what pays</small></h2>
    <div class="wrap"><table>
      <thead><tr><th class="l">strategy</th><th>#</th><th>episodes</th><th title="mean of (miner pass − baseline pass) per instance">Δ vs baseline</th><th title="one-sided 90% lower bound of Δ vs baseline">Δc</th><th title="efficiency term admitted">gate</th><th title="passed the published check while failing the withheld one">overfit</th><th title="disqualified episodes">dq</th><th>score</th><th>weight</th></tr></thead>
      <tbody>{"".join(body) or '<tr><td class="empty" colspan="10">no strategies were sealed</td></tr>'}</tbody>
    </table></div>
  </section>
  <section class="panel">
    <h2>Families</h2>
    <div class="wrap"><table>
      <thead><tr><th class="l">family</th><th>baseline n</th><th>baseline</th><th>canon</th><th title="canon's Δc against the baseline">Δc canon</th><th class="l">label</th></tr></thead>
      <tbody>{families or '<tr><td class="empty" colspan="6">—</td></tr>'}</tbody>
    </table></div>
  </section>
  <p class="small muted">Artefacts: {artefacts}. Every withheld half and its salt is in <code>reveal.json</code>; <code>HMAC(salt, withheld)</code> must equal the commitment published when the round opened.</p>
</main>
</body>
</html>
"""


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--close", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--meta", help="the round's entry in rounds/index.json, as a JSON file or inline")
    a = ap.parse_args(argv)
    meta = None
    if a.meta:
        meta = json.loads(Path(a.meta).read_text()) if Path(a.meta).exists() else json.loads(a.meta)
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    page = render(json.loads(Path(a.close).read_text()), meta)
    (out / "index.html").write_text(page)
    print(f"{out / 'index.html'} ({len(page)} bytes)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
