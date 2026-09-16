"""S1: a strategy is prose about how to work, not the round's answers pasted in."""

from __future__ import annotations

import base64
import json
from pathlib import Path

from sh.validator import similarity as S

REFERENCE = "\n".join(
    f"python3 - <<'PY'\nimport json\nrows = json.load(open('/task_file/input/data_{i}.json'))\n"
    f"summary_{i} = sorted(r['amount_cents'] for r in rows if r['status'] == 'settled')\n"
    f"open('/task_file/output/report_{i}.md', 'w').write('total: ' + str(sum(summary_{i})))\nPY"
    for i in range(12)
)
TESTS = "\n".join(
    f"def test_total_{i}():\n    assert Path('/task_file/output/report_{i}.md').read_text().startswith('total: ')"
    for i in range(12)
)
PROMPT = "Produce /task_file/output/report_0.md with the settled total. Do not modify the inputs."


def _round(tmp_path: Path) -> Path:
    rd = tmp_path / "r0007"
    for sub in ("private", "withheld", "tasks"):
        (rd / sub).mkdir(parents=True)
    (rd / "private" / "t.json").write_text(json.dumps({"solutions": {"reference": REFERENCE, "alternates": []}}))
    (rd / "withheld" / "t.json").write_text(
        json.dumps({"assets": {"tests/test_state.py": base64.b64encode(TESTS.encode()).decode()}})
    )
    (rd / "tasks" / "t.json").write_text(json.dumps({"prompt": PROMPT}))
    return rd


def test_instruction_style_prose_is_not_refused(tmp_path):
    refs = S.load(_round(tmp_path))
    soul = (
        "Read the whole instruction first. Inspect every input's real shape before writing code against it.\n"
        "Write each deliverable exactly where the instruction says, then open it and check it field by field.\n"
        "Produce /task_file/output/report_0.md with the settled total. Do not modify the inputs.\n"  # quoting the task
    )
    assert refs.refuse(soul) is None


def test_a_pasted_solution_is_refused_even_inside_markdown_fences(tmp_path):
    refs = S.load(_round(tmp_path))
    soul = "# Strategy\n\nFor this round, run exactly:\n\n```bash\n" + REFERENCE + "\n```\n"
    assert refs.refuse(soul).startswith("S1 bundle reproduces this round's reference answers")


def test_a_verifier_reflowed_into_a_paragraph_is_refused(tmp_path):
    refs = S.load(_round(tmp_path))
    assert refs.refuse("The checker wants: " + " ".join(TESTS.split())) is not None


def test_a_round_without_private_answers_checks_nothing(tmp_path):
    rd = tmp_path / "r0001"
    (rd / "tasks").mkdir(parents=True)
    assert not S.load(rd) and S.load(rd).refuse("anything at all") is None
