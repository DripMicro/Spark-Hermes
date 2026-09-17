"""One call at a time per episode: the budget is exact, and a burst of parallel calls on one token cannot hold the
proxy or the engine against other episodes."""

from __future__ import annotations

import threading
import time

import sh.validator.proxy as P


def test_calls_of_one_episode_are_serialized_and_a_burst_beyond_the_queue_is_refused():
    gate = P.Gate()
    first = gate.enter("ep-1")
    assert first is not None
    entered, refused = [], []

    def call():
        lock = gate.enter("ep-1")
        if lock is None:
            refused.append(1)
            return
        entered.append(time.monotonic())
        gate.leave("ep-1", lock)

    threads = [threading.Thread(target=call) for _ in range(6)]
    for t in threads:
        t.start()
    time.sleep(0.2)
    assert entered == [] and len(refused) >= 6 - P.MAX_WAITING  # queued behind the call in flight, the rest refused
    other = gate.enter("ep-2")  # another episode is not held up
    assert other is not None
    gate.leave("ep-2", other)
    gate.leave("ep-1", first)
    for t in threads:
        t.join(timeout=2)
    assert len(entered) + len(refused) == 6 and len(entered) <= P.MAX_WAITING
