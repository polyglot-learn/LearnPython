"""Barriers: hold every thread at a line until all of them arrive.

A barrier is a meeting point. N workers each do some work, call wait, and block
there; only when the Nth arrives does the barrier release all of them together
to start the next phase. The guarantee is that no thread begins phase k+1 until
every thread has finished phase k, which is exactly what you want for staged
computations where each stage reads the previous stage's output.

`threading.Barrier` gives this out of the box and is reusable: after releasing,
it resets for the next round, and it hands exactly one arriving thread the
distinguished return value so a single thread can run the between-phase cleanup.
Below we also build the same thing by hand from a Condition with a generation
counter — the counter is what makes it reusable, so a fast thread looping into
the next phase cannot be mistaken for a straggler still in the previous one.
"""

import threading


class ReusableBarrier:
    """Hand-built cyclic barrier: the generation counter makes reuse safe."""

    def __init__(self, parties: int) -> None:
        self.parties = parties
        self._count = 0
        self._generation = 0
        self._cond = threading.Condition()

    def wait(self) -> None:
        with self._cond:
            gen = self._generation
            self._count += 1
            if self._count == self.parties:
                # Last one in: open the gate and start a fresh generation.
                self._count = 0
                self._generation += 1
                self._cond.notify_all()
            else:
                # Wait until the generation advances, not merely for a notify:
                # guards against spurious wakeups and fast re-entry.
                while gen == self._generation:
                    self._cond.wait()


def run_phases(barrier: object, parties: int, phases: int) -> list[list[int]]:
    """Each worker records the phase it is in right after crossing a barrier."""
    arrivals: list[list[int]] = [[] for _ in range(phases)]
    guard = threading.Lock()

    def worker(wid: int) -> None:
        for phase in range(phases):
            # do phase work here...
            barrier.wait()  # type: ignore[attr-defined]
            with guard:
                arrivals[phase].append(wid)

    threads = [threading.Thread(target=worker, args=(i,)) for i in range(parties)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return arrivals


def main() -> None:
    parties, phases = 4, 3

    std = threading.Barrier(parties)
    arrivals = run_phases(std, parties, phases)
    for i, seen in enumerate(arrivals):
        print(f"threading.Barrier phase {i}: all arrived = "
              f"{sorted(seen) == list(range(parties))}")

    hand = ReusableBarrier(parties)
    arrivals = run_phases(hand, parties, phases)
    for i, seen in enumerate(arrivals):
        print(f"ReusableBarrier   phase {i}: all arrived = "
              f"{sorted(seen) == list(range(parties))}")

    # The distinguished return value lets exactly one thread run phase cleanup.
    b = threading.Barrier(parties)
    leaders: list[int] = []
    lead_lock = threading.Lock()

    def elect(wid: int) -> None:
        idx = b.wait()  # one thread gets 0, used to pick a leader
        if idx == 0:
            with lead_lock:
                leaders.append(wid)

    threads = [threading.Thread(target=elect, args=(i,)) for i in range(parties)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"exactly one leader elected per round: {len(leaders) == 1}")

    print("\nedge cases")
    solo = ReusableBarrier(1)
    solo.wait()  # a 1-party barrier releases immediately
    print("  1-party barrier releases the lone thread at once")
    print(f"  live threads at exit: {threading.active_count()} (only MainThread)")


if __name__ == "__main__":
    main()
