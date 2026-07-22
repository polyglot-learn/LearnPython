"""Locks, queues, and why `counter += 1` is not atomic.

`counter += 1` compiles to load, add, store. The GIL can switch threads between
those bytecodes, so two threads can read the same value and one increment is
lost. The GIL prevents interpreter corruption, not data races in your logic.

Tools, in the order you should reach for them:
  Queue      hand work between threads; no explicit locking needed
  Lock       mutual exclusion for a critical section
  RLock      re-entrant, for recursive or nested acquisition
  Event      one-shot signal between threads
  Semaphore  cap the number of concurrent holders
"""

import threading
from queue import Queue


def race() -> int:
    counter = 0

    def bump() -> None:
        nonlocal counter
        for _ in range(100_000):
            counter += 1  # load, add, store — interruptible

    threads = [threading.Thread(target=bump) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter


def locked() -> int:
    counter = 0
    lock = threading.Lock()

    def bump() -> None:
        nonlocal counter
        for _ in range(100_000):
            with lock:  # always use `with`: releases even on an exception
                counter += 1

    threads = [threading.Thread(target=bump) for _ in range(4)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    return counter


def worker_pool() -> list[int]:
    """Queue-based fan-out: no shared mutable state to protect."""
    jobs: Queue[int | None] = Queue()
    results: Queue[int] = Queue()

    def worker() -> None:
        while (job := jobs.get()) is not None:
            results.put(job * job)
            jobs.task_done()
        jobs.task_done()

    threads = [threading.Thread(target=worker) for _ in range(3)]
    for t in threads:
        t.start()
    for n in range(10):
        jobs.put(n)
    for _ in threads:
        jobs.put(None)  # one sentinel per worker
    for t in threads:
        t.join()
    return sorted(results.queue)


def main() -> None:
    expected = 400_000
    lost = race()
    print(f"unsynchronised: {lost} (expected {expected}, "
          f"{'lost updates' if lost != expected else 'got lucky this run'})")
    print(f"with a Lock:    {locked()}")
    print(f"queue workers:  {worker_pool()}")

    # An Event is the clean way to signal a thread to stop.
    stop = threading.Event()
    ticks = 0

    def tick() -> None:
        nonlocal ticks
        while not stop.wait(0.01):
            ticks += 1

    t = threading.Thread(target=tick)
    t.start()
    stop.wait(0.05)
    stop.set()
    t.join()
    print(f"event-stopped thread ticked {ticks} times")


if __name__ == "__main__":
    main()
