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


def test_a_bug_fix_round_is_checked_against_the_fixed_code_not_the_repository_or_its_tests(tmp_path):
    """swe_fix: the reference is a diff whose context is the repository's own code, and the grader's assets are the
    repository's tests. Quoting either is not reproducing an answer; pasting the lines the bug replaced is."""
    fixed = "\n".join(
        f"        self._tokens_{i} = token_types[{i}] if token_types else default_token_{i}" for i in range(10)
    )
    context = "\n".join(f"    def validate_request_number_{i}(self, request, scopes=None):" for i in range(10))
    rd = tmp_path / "r0008"
    for sub in ("private", "withheld", "tasks"):
        (rd / sub).mkdir(parents=True)
    (rd / "private" / "t.json").write_text(
        json.dumps({"solutions": {"reference": "git apply -R <<EOF\n" + context + "\nEOF", "answer": fixed}})
    )
    (rd / "withheld" / "t.json").write_text(
        json.dumps(
            {
                "assets": {"swe/files/tests/test_x.py": base64.b64encode(TESTS.encode()).decode()},
                "assets_are_answers": False,
            }
        )
    )
    (rd / "tasks" / "t.json").write_text(json.dumps({"prompt": "Fix the bug."}))
    refs = S.load(rd)
    assert refs.refuse("Read the code around the failure:\n" + context + "\n" + TESTS) is None
    assert refs.refuse("Apply this:\n" + fixed) is not None


def test_quoting_a_preview_is_not_reproducing_an_answer(tmp_path):
    """swe_fix shows miners previews; text from a preview's issue is what they were given, not an answer."""
    rd = tmp_path / "r0009"
    for sub in ("private", "tasks", "preview"):
        (rd / sub).mkdir(parents=True)
    quoted = "\n".join(f"        self.width_{i} = compute_width(self.chars_{i}, self.font_{i})" for i in range(10))
    (rd / "private" / "t.json").write_text(json.dumps({"solutions": {"reference": "x", "answer": quoted}}))
    (rd / "tasks" / "t.json").write_text(json.dumps({"prompt": "hidden"}))
    (rd / "preview" / "p.json").write_text(json.dumps({"prompt": "The issue shows:\n" + quoted}))
    assert S.load(rd).refuse("As the practice issue shows:\n" + quoted) is None


def test_a_bug_that_only_added_code_has_no_answer_and_its_diff_is_never_matched(tmp_path):
    rd = tmp_path / "r0010"
    for sub in ("private", "tasks"):
        (rd / sub).mkdir(parents=True)
    context = "\n".join(f"    def validate_request_number_{i}(self, request, scopes=None):" for i in range(10))
    (rd / "private" / "t.json").write_text(
        json.dumps({"solutions": {"reference": "git apply -R <<EOF\n" + context + "\nEOF", "answer": ""}})
    )
    (rd / "tasks" / "t.json").write_text(json.dumps({"prompt": "Fix the bug."}))
    assert S.load(rd).refuse("Look at:\n" + context) is None
