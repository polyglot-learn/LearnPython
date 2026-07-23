"""Deadlock: two threads each holding what the other needs, forever.

Give two threads two locks and let them acquire in opposite orders. Thread A
takes lock 1 then reaches for lock 2; thread B takes lock 2 then reaches for
lock 1. If both grab their first lock before either grabs its second, each now
waits on a lock the other holds and neither can proceed. A barrier makes that
interleaving happen every run, so the deadlock is deterministic rather than a
rare fluke.

Two standard cures. First, impose a global order: every thread acquires locks in
the same fixed sequence (here by id), which makes the circular wait impossible,
so the same workload completes. Second, acquire with a timeout: a thread that
cannot get the second lock in time backs off, releases what it holds, and
retries instead of blocking forever. This file uses timeouts throughout as a
watchdog so the demonstration always terminates and never wedges the process.
"""

import threading

TIMEOUT = 0.5  # watchdog: no acquire ever blocks longer than this


def deadlocking_run() -> bool:
    """Force the classic deadlock; report whether it occurred (it will)."""
    l1, l2 = threading.Lock(), threading.Lock()
    gate = threading.Barrier(2)
    stuck = {"a": False, "b": False}

    def grab(first: threading.Lock, second: threading.Lock, who: str) -> None:
        first.acquire()
        try:
            gate.wait()  # ensure both hold their first lock before the second
            if second.acquire(timeout=TIMEOUT):
                second.release()
            else:
                stuck[who] = True  # timed out: the other thread has it
        finally:
            first.release()

    ta = threading.Thread(target=grab, args=(l1, l2, "a"))
    tb = threading.Thread(target=grab, args=(l2, l1, "b"))
    ta.start()
    tb.start()
    ta.join()
    tb.join()
    return stuck["a"] and stuck["b"]


def ordered_run() -> bool:
    """Same workload, but both threads lock in a single global order."""
    l1, l2 = threading.Lock(), threading.Lock()
    gate = threading.Barrier(2)
    completed = {"a": False, "b": False}

    # Fixed order by identity breaks the circular wait: nobody holds lock B
    # while waiting for lock A if everyone always takes A before B.
    ordered = sorted((l1, l2), key=id)

    def work(who: str) -> None:
        gate.wait()
        first, second = ordered
        with first, second:
            completed[who] = True

    ta = threading.Thread(target=work, args=("a",))
    tb = threading.Thread(target=work, args=("b",))
    ta.start()
    tb.start()
    ta.join()
    tb.join()
    return completed["a"] and completed["b"]


def timeout_escape() -> str:
    """A thread that cannot get a held lock in time backs off cleanly."""
    held = threading.Lock()
    held.acquire()  # main thread keeps it, never releasing during the attempt
    outcome = {"msg": ""}

    def try_it() -> None:
        if held.acquire(timeout=0.05):
            held.release()
            outcome["msg"] = "acquired"
        else:
            outcome["msg"] = "gave up after timeout, no hang"

    t = threading.Thread(target=try_it)
    t.start()
    t.join()
    held.release()
    return outcome["msg"]


def main() -> None:
    print(f"opposite lock order deadlocks: {deadlocking_run()} "
          "(both threads timed out on the second lock)")
    print(f"global lock ordering completes: {ordered_run()} "
          "(circular wait is impossible)")
    print(f"timeout escape: {timeout_escape()!r}")

    print("\nedge cases")
    # Ordered acquisition is fine even under repeated contention.
    all_ok = all(ordered_run() for _ in range(5))
    print(f"  ordered run is reliable across repeats: {all_ok}")
    print(f"  live threads at exit: {threading.active_count()} (only MainThread)")


if __name__ == "__main__":
    main()
