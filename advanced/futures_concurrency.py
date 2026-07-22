"""`concurrent.futures` — one API over threads and processes.

An Executor takes callables and returns Futures. Swap ThreadPoolExecutor for
ProcessPoolExecutor and the code is unchanged; only the isolation model and the
cost of moving data differ.

Two submission styles:
    map      results in input order, exceptions surface on iteration
    submit   returns a Future each; pair with as_completed to handle results
             as they arrive, which is what you want when latencies differ

An exception inside a worker is stored in its Future and re-raised when you
call `.result()`. A Future you never inspect silently swallows the failure.
"""

import time
from concurrent.futures import (
    ALL_COMPLETED,
    FIRST_EXCEPTION,
    ThreadPoolExecutor,
    as_completed,
    wait,
)


def fetch(name: str, delay: float) -> str:
    time.sleep(delay)
    if name == "bad":
        raise ValueError("upstream refused")
    return f"{name} after {delay}s"


def main() -> None:
    jobs = [("slow", 0.15), ("medium", 0.08), ("fast", 0.02)]

    print("map — results come back in submission order:")
    start = time.perf_counter()
    with ThreadPoolExecutor(max_workers=3) as pool:
        for result in pool.map(lambda job: fetch(*job), jobs):
            print(f"  {result}")
    print(f"  elapsed {time.perf_counter() - start:.2f}s (vs 0.25s sequential)")

    print("as_completed — handle each result the moment it lands:")
    with ThreadPoolExecutor(max_workers=3) as pool:
        futures = {pool.submit(fetch, name, delay): name for name, delay in jobs}
        for future in as_completed(futures):
            print(f"  {futures[future]} -> {future.result()}")

    print("exceptions travel inside the Future:")
    with ThreadPoolExecutor() as pool:
        future = pool.submit(fetch, "bad", 0.01)
        print(f"  done={future.done()} before result()")
        try:
            future.result()
        except ValueError as exc:
            print(f"  re-raised on result(): {exc}")
        print(f"  future.exception() -> {future.exception()!r}")

    print("wait() with FIRST_EXCEPTION:")
    with ThreadPoolExecutor() as pool:
        futures = [pool.submit(fetch, n, d) for n, d in [("bad", 0.01), ("ok", 0.2)]]
        done, pending = wait(futures, return_when=FIRST_EXCEPTION)
        print(f"  done={len(done)} pending={len(pending)}")
        for f in futures:
            f.cancel()

    print("timeouts and cancellation:")
    with ThreadPoolExecutor() as pool:
        future = pool.submit(fetch, "slow", 1.0)
        try:
            future.result(timeout=0.05)
        except TimeoutError:
            print("  timed out waiting; the worker itself keeps running")
        print(f"  cancel() after start -> {future.cancel()}")
        wait([future], return_when=ALL_COMPLETED)

    print("callbacks fire when the future settles:")
    with ThreadPoolExecutor() as pool:
        f = pool.submit(fetch, "cb", 0.01)
        f.add_done_callback(lambda fut: print(f"  callback saw: {fut.result()}"))


if __name__ == "__main__":
    main()
