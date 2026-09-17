"""Does a bundle reproduce the round's answers? (the seal's S1 check)

The tasks come from public datasets whose solutions are public too (FACET-Terminal's references and verifiers,
SWE-smith's bug diffs), and miners see tasks — or, for swe_fix, sibling bugs from the same repositories — for the
whole window. A strategy is prose, but prose can carry a pasted solution as a code block, and neither the lint nor
the overfit rule can see it: the reference passes every check.

This check compares a bundle with what the validator privately holds for the round — every task's reference
and alternate solutions and its verifier — and refuses a bundle that carries a material share of them. Two
signals, both on normalised text so indentation and markdown fences do not hide a paste:

  * **lines** — distinct non-trivial lines (≥ 24 characters) the bundle shares with a reference;
  * **shingles** — distinct 12-token runs the bundle shares with a reference, which catches a paste reflowed
    into paragraphs.

Anything that also appears in a task's prompt, or in a preview's, is excluded: quoting what a miner was given is not
reproducing an answer. Instruction-style prose shares essentially nothing with a solution script.
"""

from __future__ import annotations

import base64
import json
import re
from pathlib import Path

MIN_LINE = 24
SHINGLE = 12
MAX_LINES = 8  # a bundle sharing more distinct solution lines than this is refused
MAX_SHINGLES = 40  # ... or more distinct 12-token runs than this
_TOKEN = re.compile(r"[A-Za-z0-9_]+|[^\sA-Za-z0-9_]")


def _lines(text: str) -> set[str]:
    out = set()
    for raw in text.splitlines():
        line = " ".join(raw.strip().strip("`").split()).lower()
        if len(line) >= MIN_LINE:
            out.add(line)
    return out


def _shingles(text: str) -> set[tuple[str, ...]]:
    toks = [t.lower() for t in _TOKEN.findall(text)]
    return {tuple(toks[i : i + SHINGLE]) for i in range(len(toks) - SHINGLE + 1)}


class References:
    """The round's private answers, prepared once per seal."""

    def __init__(self, answers: list[str], prompts: list[str]):
        prompt_lines = set().union(*(_lines(p) for p in prompts)) if prompts else set()
        prompt_shingles = set().union(*(_shingles(p) for p in prompts)) if prompts else set()
        self.lines = set().union(*(_lines(a) for a in answers)) - prompt_lines if answers else set()
        self.shingles = set().union(*(_shingles(a) for a in answers)) - prompt_shingles if answers else set()

    def __bool__(self) -> bool:
        return bool(self.lines or self.shingles)

    def overlap(self, bundle_text: str) -> dict:
        lines = _lines(bundle_text) & self.lines
        shingles = _shingles(bundle_text) & self.shingles
        return {"lines": len(lines), "shingles": len(shingles), "sample": sorted(lines)[:3]}

    def refuse(self, bundle_text: str) -> str | None:
        """The refusal reason, or None when the bundle does not reproduce the round's answers."""
        o = self.overlap(bundle_text)
        if o["lines"] > MAX_LINES or o["shingles"] > MAX_SHINGLES:
            return (
                f"S1 bundle reproduces this round's reference answers ({o['lines']} solution lines, "
                f"{o['shingles']} {SHINGLE}-token runs in common)"
            )
        return None


def load(round_dir: Path) -> References:
    """References from a minted round directory: private/ (solutions), withheld/ (verifier assets), tasks/ (prompts)."""
    answers: list[str] = []
    for p in sorted((round_dir / "private").glob("*.json")) if (round_dir / "private").is_dir() else []:
        sol = json.loads(p.read_text()).get("solutions", {})
        if sol.get("answer"):  # the correct code as a miner would paste it (swe_fix: the lines its bug replaced) —
            answers.append(sol["answer"])  # its reference is a diff whose context is the repository's own code
        else:
            answers += [sol.get("reference") or "", *(sol.get("alternates") or [])]
    for p in sorted((round_dir / "withheld").glob("*.json")) if (round_dir / "withheld").is_dir() else []:
        record = json.loads(p.read_text())
        if record.get("assets_are_answers", True):  # a verifier is an answer; a repository's own tests are not
            for b64 in (record.get("assets") or {}).values():
                answers.append(base64.b64decode(b64).decode("utf-8", "replace"))
    # what miners were given: the tasks, or the previews they saw in their place (swe_fix) — quoting either is fair
    prompts = [
        json.loads(p.read_text()).get("prompt", "")
        for sub in ("tasks", "preview")
        for p in sorted((round_dir / sub).glob("*.json"))
    ]
    return References([a for a in answers if a], prompts)


def bundle_text(files: dict[str, bytes]) -> str:
    return "\n".join(
        data.decode("utf-8", "replace") for path, data in sorted(files.items()) if path != "attestation.json"
    )
