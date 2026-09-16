"""The scorecard a miner gets back after a round closes (FR-TRN).

A miner is told three things, and each exists because withholding it would make the result unfalsifiable:

  * **what their bundle did** on every instance, against what the baseline did on the *same* instance;
  * **why the number is what it is** — the mean, the standard error including the reference term, and the
    one-sided bound that is actually paid;
  * **the revealed withheld half and its salt**, so they can recompute the commitment themselves and confirm
    the criteria were fixed before they submitted.

    python -m sh.cli.scorecard --close DIR/close.json --hotkey 5F... [--markdown]
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


def render(close: dict, hotkey: str, reveal: dict | None = None) -> str:
    score = close.get("scores", {}).get(hotkey)
    if score is None:
        known = ", ".join(sorted(close.get("scores", {}))) or "none"
        return f"No episodes for `{hotkey}` in round `{close.get('round_id')}`. Scored hotkeys: {known}."

    weight = close.get("weights", {}).get(hotkey, 0.0)
    lines = [
        f"## Round `{close.get('round_id')}` — `{hotkey}`",
        "",
        f"**weight {weight:.4f}**"
        + (f" · score {score['score']:.4f}" if score["score"] else " · scored nothing this round"),
        "",
        "| | |",
        "|---|---|",
        f"| episodes | {score['n']} |",
        f"| mean d (you − baseline, same instances) | {score.get('mean_d', 0) or 0:+.4f} |",
        f"| standard error (incl. reference term) | {score.get('se') if score.get('se') is not None else '—'} |",
        f"| Δc (one-sided 90 % lower bound — what pays) | {score['delta_c']:.4f} |",
        f"| correctness gate | {'passed' if score['gate'] else 'not passed'} |",
        f"| Δe | {score['delta_e'] or '—'} |",
        f"| overfit rate | {score['overfit_rate']:.2f} |",
        f"| disqualified episodes | {score['dq']} |",
    ]
    if score.get("reason"):
        lines += ["", f"> **Paid nothing:** {score['reason']}"]

    lines += [
        "",
        "`mean d` is your pass rate minus the pinned model's pass rate on the *same instances*, with no "
        "strategy. Passing tasks is not the achievement — beating that baseline is. `Δc` is the lower bound of "
        "that difference, so beating the baseline on average is not enough to be *paid* for beating it.",
    ]

    families = close.get("family_stats", {})
    if families:
        lines += [
            "",
            "### The baseline you were measured against",
            "",
            "| family | null n | null p | canon p | Δc canon | label |",
            "|---|---|---|---|---|---|",
        ]
        for name, record in sorted(families.items()):
            null, canon = record["null"], record["canon"]
            fmt = lambda v: "—" if v is None else f"{v:.2f}"  # noqa: E731
            lines.append(
                f"| `{name}` | {null['n']} | {fmt(null['p'])} | {fmt(canon['p'])} | "
                f"{canon.get('delta_c') if canon.get('delta_c') is not None else '—'} | {record['label']} |"
            )

    verified = close.get("commitments_verified", {})
    checked = {t: v for t, v in verified.items() if v is not None}
    if checked:
        ok = all(checked.values())
        lines += [
            "",
            "### Check the grading yourself",
            "",
            f"{sum(1 for v in checked.values() if v)} of {len(checked)} withheld commitments re-verified at "
            f"close: **{'all match' if ok else 'MISMATCH — do not trust this round'}**.",
            "",
            "Each instance's withheld half was committed to *before* submissions opened, as "
            "`hmac-sha256(salt, canonical_json(withheld))`, and the commitment was published with the task. The "
            "salt and the half itself are published now, in `reveal.json`. Recompute it and confirm the "
            "criteria you were graded against are the ones that were fixed in advance:",
            "",
            "```python",
            "import hashlib, hmac, json",
            'salt, withheld = reveal[task_id]["salt"], reveal[task_id]["withheld"]',
            'body = json.dumps(withheld, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()',
            '"hmac-sha256:" + hmac.new(bytes.fromhex(salt), body, hashlib.sha256).hexdigest()',
            "```",
        ]
        if reveal:
            lines += [
                "",
                f"<details><summary>Revealed withheld halves ({len(reveal)})</summary>",
                "",
                "```json",
                json.dumps(reveal, indent=1)[:4000],
                "```",
                "",
                "</details>",
            ]
    return "\n".join(lines)


def main(argv=None) -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--close", required=True)
    ap.add_argument("--hotkey", required=True)
    ap.add_argument("--reveal")
    ap.add_argument("--out")
    a = ap.parse_args(argv)
    close = json.loads(Path(a.close).read_text())
    reveal = json.loads(Path(a.reveal).read_text()) if a.reveal else None
    text = render(close, a.hotkey, reveal)
    if a.out:
        Path(a.out).write_text(text)
    print(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
