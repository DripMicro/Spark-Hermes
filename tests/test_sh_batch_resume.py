"""B6: the round queue survives a kill. Resuming re-grades what crashed and re-runs nothing that finished."""

from __future__ import annotations

import json
from pathlib import Path

import sh.validator.batch as batch

TASK = {"task_id": "t-1", "timeout_s": 60, "published": {"predicates": []}}


def _round(tmp_path: Path) -> Path:
    rd = tmp_path / "round"
    (rd / "tasks").mkdir(parents=True)
    (rd / "withheld").mkdir()
    (rd / "tasks" / "t-1.json").write_text(json.dumps(TASK))
    return rd


def test_a_finished_episode_is_never_run_twice(tmp_path, monkeypatch):
    runs = []

    def fake_run(task, bundle, image, inference, ep, **k):
        runs.append(ep)
        Path(ep).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(batch, "run_episode", fake_run)
    monkeypatch.setattr(batch, "grade", lambda ep, *a, **k: {"verified_success": True, "episode_dir": str(ep)})
    out = tmp_path / "out"
    first = batch.one(TASK, None, "null", None, "img", "url", out)
    again = batch.one(TASK, None, "null", None, "img", "url", out)
    assert len(runs) == 1 and again == first  # second call is a no-op replay


def test_an_episode_that_ran_but_failed_to_grade_is_only_re_graded(tmp_path, monkeypatch):
    """The V5 failure mode: grading crashed on 24 episodes that had each cost a GPU minute."""
    out = tmp_path / "out"
    ep = out / "null" / "t-1"
    ep.mkdir(parents=True)
    ep.joinpath("finish.json").write_text(json.dumps({"stage": "done", "api_calls": 5}))
    runs = []
    monkeypatch.setattr(batch, "run_episode", lambda *a, **k: runs.append(1))
    monkeypatch.setattr(batch, "grade", lambda *a, **k: {"verified_success": True})
    rec = batch.one(TASK, None, "null", None, "img", "url", out)
    assert runs == [] and rec["verified_success"]
    assert json.loads((ep / "episode.json").read_text())["verified_success"]


def test_a_half_written_episode_is_run_again(tmp_path, monkeypatch):
    out = tmp_path / "out"
    ep = out / "null" / "t-1"
    ep.mkdir(parents=True)
    ep.joinpath("finish.json").write_text(json.dumps({"stage": "no_finish"}))  # killed mid-run
    runs = []
    monkeypatch.setattr(batch, "run_episode", lambda *a, **k: runs.append(1))
    monkeypatch.setattr(batch, "grade", lambda *a, **k: {"verified_success": False})
    batch.one(TASK, None, "null", None, "img", "url", out)
    assert runs == [1]


def test_a_void_episode_is_not_cached_so_a_resume_re_runs_it(tmp_path, monkeypatch):
    """A provider outage must not be frozen into the archive as a failed attempt."""
    out = tmp_path / "out"
    runs = []

    def fake_run(task, bundle, image, inference, ep, **k):
        runs.append(ep)
        Path(ep).mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(batch, "run_episode", fake_run)
    monkeypatch.setattr(
        batch, "grade", lambda *a, **k: {"verified_success": False, "void": True, "void_reason": "overloaded"}
    )
    rec = batch.one(TASK, None, "null", None, "img", "url", out)
    assert rec["void"]
    assert not (out / "null" / "t-1" / "episode.json").exists()
    batch.one(TASK, None, "null", None, "img", "url", out)
    assert len(runs) == 2  # re-run, not replayed


def test_a_void_episode_that_finished_is_moved_aside_and_run_again(tmp_path, monkeypatch):
    """A real run writes finish.json with stage "done" even when the provider refused every call. Left in place,
    a resume would only re-grade that trajectory — void again, forever; round r0003 lost a third of its episodes."""
    out = tmp_path / "out"
    runs = []

    def fake_run(task, bundle, image, inference, ep, **k):
        runs.append(ep)
        Path(ep).mkdir(parents=True, exist_ok=True)
        (Path(ep) / "finish.json").write_text(json.dumps({"stage": "done"}))

    grades = iter([{"verified_success": False, "void": True, "void_reason": "overloaded"}, {"verified_success": True}])
    monkeypatch.setattr(batch, "run_episode", fake_run)
    monkeypatch.setattr(batch, "grade", lambda *a, **k: next(grades))
    assert batch.one(TASK, None, "null", None, "img", "url", out)["void"]
    assert (out / "null" / "t-1.void-1" / "finish.json").exists() and not (out / "null" / "t-1").exists()
    assert batch.one(TASK, None, "null", None, "img", "url", out)["verified_success"]
    assert len(runs) == 2 and (out / "null" / "t-1" / "episode.json").exists()


def test_the_batch_re_runs_void_episodes_in_later_passes(tmp_path, monkeypatch):
    rd = _round(tmp_path)
    out = tmp_path / "out"
    outcomes = {"null": iter([True, False]), "canon": iter([False])}  # null is void once, then graded

    def fake_one(task, withheld, surface, bundle, *a, **k):
        void = next(outcomes[surface])
        rec = {
            "surface": surface,
            "task_id": task["task_id"],
            "void": void,
            "void_reason": "overloaded" if void else None,
        }
        return rec | {
            "verified_success": not void,
            "overfit": False,
            "disqualified": False,
            "api_calls": 1,
            "wall_s": 1.0,
            "partial": False,
            "timed_out": False,
            "self_checked": False,
        }

    monkeypatch.setattr(batch, "one", fake_one)
    monkeypatch.setattr(batch.time, "sleep", lambda s: None)
    rc = batch.main(
        [
            "--round",
            str(rd),
            "--surfaces",
            "null,canon=" + str(tmp_path),
            "--image",
            "i",
            "--inference",
            "u",
            "--out",
            str(out),
            "--void-retries",
            "2",
        ]
    )
    summary = json.loads((out / "summary.json").read_text())
    assert rc == 0 and summary["episodes"] == 2 and summary["per_surface"]["null"]["n"] == 1
