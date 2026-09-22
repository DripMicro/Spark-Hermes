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


def test_a_void_king_episode_is_never_exported(tmp_path):
    from sh.exports.build import build

    rd = tmp_path / "round"
    (rd / "tasks").mkdir(parents=True)
    (rd / "close.json").write_text(json.dumps({"tasks": []}))
    eps = rd / "episodes" / "5K" / "t0"
    eps.mkdir(parents=True)
    (eps / "episode.json").write_text(
        json.dumps({"task_id": "t0", "surface": "5K", "verified_success": True, "void": True})
    )
    (eps / "trajectory.json").write_text(
        json.dumps([{"from": "human", "value": "fix it"}, {"from": "gpt", "value": "done"}])
    )
    m = build(rd, rd / "episodes", rd / "close.json", tmp_path / "out", king="5K")
    assert m["sft_rows"] == 0 and m["gates"]["void"] == 1


def test_a_dpo_pair_shares_the_kings_system_turn(tmp_path):
    from sh.exports.build import build

    rd = tmp_path / "round"
    (rd / "tasks").mkdir(parents=True)
    (rd / "tasks" / "t0.json").write_text(json.dumps({"task_id": "t0", "prompt": "fix it", "tools": []}))
    (rd / "close.json").write_text(json.dumps({"tasks": ["t0"]}))
    for surface, credit, sp in (("5K", 1.0, "KING SOUL"), ("null", 0.0, "GENERIC")):
        d = rd / "episodes" / surface / "t0"
        d.mkdir(parents=True)
        (d / "episode.json").write_text(
            json.dumps({"task_id": "t0", "surface": surface, "credit": credit, "verified_success": credit == 1.0})
        )
        (d / "system_prompt.txt").write_text(sp)
        (d / "trajectory.json").write_text(
            json.dumps(
                [
                    {"from": "system", "value": sp},
                    {"from": "human", "value": "fix it"},
                    {"from": "gpt", "value": f"by {surface}"},
                ]
            )
        )
    build(rd, rd / "episodes", rd / "close.json", tmp_path / "out", king="5K")
    pairs = [json.loads(x) for x in (tmp_path / "out" / "dpo.jsonl").read_text().splitlines()]
    assert len(pairs) == 1
    p = pairs[0]
    assert p["chosen"][0] == {"from": "system", "value": "KING SOUL"}
    assert p["rejected"][0] == {"from": "system", "value": "KING SOUL"}  # not GENERIC: the confound is removed
    assert p["rejected"][-1]["value"] == "by null"  # but the rejected trajectory is still null's


def test_the_crowned_prose_never_enters_an_exported_row(tmp_path):
    """The export is public. The captured system turn is what the episode really ran under, which on a strategy
    surface embeds that miner's bundle verbatim — publishing it would hand the crowned strategy to every rival."""
    import json as _json

    from sh.exports.build import _bundle_secrets, _rows_for

    bundle = tmp_path / "bundle"
    bundle.mkdir()
    soul = "# Soul\n\nA distinctive line of the crowned strategy that rivals must not get to read.\n"
    (bundle / "SOUL.md").write_text(soul)
    secrets = _bundle_secrets(bundle)

    ep = tmp_path / "ep"
    ep.mkdir()
    (ep / "trajectory.json").write_text(
        _json.dumps([{"from": "system", "value": "generic"}, {"from": "gpt", "value": "fixed it"}])
    )
    (ep / "system_prompt.txt").write_text("You are Hermes.\n\n" + soul)  # what the episode actually ran under

    row = _rows_for(ep, {"task_id": "t"}, {}, "SURFACE-LESS-PROMPT", secrets)
    assert row["conversations"][0]["value"] == "SURFACE-LESS-PROMPT"  # fell back rather than publish the bundle
    assert "distinctive line of the crowned strategy" not in _json.dumps(row)
    # and with no bundle named, the captured prompt is still preferred, as before
    assert _rows_for(ep, {"task_id": "t"}, {}, "x")["conversations"][0]["value"].startswith("You are Hermes.")
