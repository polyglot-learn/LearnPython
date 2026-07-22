"""The GIL: why threads help I/O and not arithmetic.

CPython's Global Interpreter Lock lets only one thread execute bytecode at a
time. A thread must hold it to run Python code, and releases it while waiting
on I/O or inside C extensions that opt out (numpy, hashlib, zlib).

So:
  I/O-bound  -> threads work. The waiting thread has released the GIL.
  CPU-bound  -> threads do not. Use processes, which each have their own
                interpreter and their own GIL.

The cost of processes is that arguments and results must be pickled and sent
between them, which is why they suit coarse-grained work.
"""

import time
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor


def cpu_work(n: int) -> int:
    """Pure bytecode: holds the GIL the whole time."""
    return sum(i * i for i in range(n))


def io_work(seconds: float) -> str:
    """time.sleep releases the GIL, so other threads run meanwhile."""
    time.sleep(seconds)
    return f"slept {seconds}s"


def timed(label: str, fn) -> None:
    start = time.perf_counter()
    fn()
    print(f"  {label:<26} {time.perf_counter() - start:.3f}s")


def main() -> None:
    n, jobs = 2_000_000, 4

    print("CPU-bound work:")
    timed("sequential", lambda: [cpu_work(n) for _ in range(jobs)])
    timed("4 threads (no speedup)", lambda: list(
        ThreadPoolExecutor(4).map(cpu_work, [n] * jobs)))
    timed("4 processes (real speedup)", lambda: list(
        ProcessPoolExecutor(4).map(cpu_work, [n] * jobs)))

    print("I/O-bound work:")
    timed("sequential", lambda: [io_work(0.1) for _ in range(jobs)])
    timed("4 threads (4x faster)", lambda: list(
        ThreadPoolExecutor(4).map(io_work, [0.1] * jobs)))

    print("rule: threads for waiting, processes for computing, asyncio for "
          "thousands of concurrent waits")


if __name__ == "__main__":
    main()  # the __main__ guard is REQUIRED for ProcessPoolExecutor
