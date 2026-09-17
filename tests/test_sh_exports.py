"""Exports: what leaves a closed round as training data, and what never does."""

from __future__ import annotations

import json

from sh.exports.build import _secrets


def test_test_ids_of_a_withheld_suite_are_not_secrets_for_the_leak_scan():
    """A verified swe_fix trajectory names the tests it ran; those ids are public at close and part of any honest
    `pytest -v`. Only salts and withheld *values* are secrets."""
    reveal = {
        "t": {
            "salt": "a" * 64,
            "withheld": {
                "predicates": [
                    ["custom", "swe_test", "tests/text/test_fonts.py::DescribeFontFiles::it_catalogs"],
                    ["custom", "facet_test", "test_state.py::test_report_has_the_total"],
                    ["digest_is", "out.txt", "b" * 64],
                ]
            },
        }
    }
    assert _secrets(reveal) == {"a" * 64, "b" * 64}


def test_a_row_carries_the_system_prompt_its_episode_ran_under(tmp_path):
    from sh.exports.build import _rows_for

    ep = tmp_path / "ep"
    ep.mkdir()
    (ep / "trajectory.json").write_text(
        json.dumps(
            [
                {"from": "system", "value": "generic"},
                {"from": "human", "value": "fix it"},
                {"from": "gpt", "value": "done"},
            ]
        )
    )
    (ep / "system_prompt.txt").write_text("the king's SOUL, as the agent saw it")
    row = _rows_for(ep, {"task_id": "t"}, {"prompt": "fix it"}, "fallback")
    assert row is not None and "the king's SOUL" in json.dumps(row) and "fallback" not in json.dumps(row)
