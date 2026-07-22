"""`async` / `await` — concurrency for waiting, not for computing.

An `async def` returns a *coroutine*: calling it runs nothing until it is
awaited or handed to the event loop. `await` says "suspend me here and let the
loop run something else until this finishes".

The key limit: asyncio is single-threaded cooperative multitasking. It makes
I/O-bound work (network, disk, timers) overlap. It does nothing for CPU-bound
work — a tight loop blocks the whole event loop, and so does any blocking call
such as `time.sleep`.
"""

import asyncio
import time


async def fetch(name: str, delay: float) -> str:
    print(f"  start {name}")
    await asyncio.sleep(delay)  # yields control; time.sleep would block
    print(f"  done  {name}")
    return f"{name} ({delay}s)"


async def sequential() -> None:
    start = time.perf_counter()
    await fetch("a", 0.2)
    await fetch("b", 0.2)
    print(f"sequential took {time.perf_counter() - start:.2f}s")


async def concurrent() -> None:
    start = time.perf_counter()
    results = await asyncio.gather(fetch("a", 0.2), fetch("b", 0.2))
    print(f"gather results: {results}")
    print(f"concurrent took {time.perf_counter() - start:.2f}s")


async def with_timeout() -> None:
    try:
        await asyncio.wait_for(fetch("slow", 1.0), timeout=0.1)
    except TimeoutError:
        print("timed out, and the task was cancelled")


async def main_async() -> None:
    coro = fetch("unawaited", 0)
    print(f"calling an async def returns {type(coro).__name__}, it has not run")
    await coro

    print("sequential:")
    await sequential()
    print("concurrent:")
    await concurrent()
    print("timeout:")
    await with_timeout()

    # TaskGroup (3.11+): structured concurrency — if one child fails, the
    # rest are cancelled and the error propagates out of the block.
    async with asyncio.TaskGroup() as tg:
        t1 = tg.create_task(fetch("x", 0.05))
        t2 = tg.create_task(fetch("y", 0.05))
    print(f"task group: {t1.result()}, {t2.result()}")


def main() -> None:
    asyncio.run(main_async())  # creates the loop, runs until complete, closes


if __name__ == "__main__":
    main()
