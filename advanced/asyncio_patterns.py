"""Production asyncio patterns: queues, bounded concurrency, retries, timeouts.

Four shapes cover most real async code:

  producer / consumer   an asyncio.Queue decouples rates; consumers are tasks,
                        and a sentinel or task cancellation ends them
  bounded fan-out       a Semaphore caps in-flight work so a burst does not
                        open ten thousand sockets at once
  retry with backoff    exponential delay plus jitter, so retries from many
                        clients do not synchronise into a thundering herd
  timeout               asyncio.timeout() (3.11+) cancels the block, and the
                        cancellation propagates into whatever it was awaiting

Everything here is cooperative: a blocking call inside a coroutine stalls the
whole loop. Push those to `asyncio.to_thread`.
"""

import asyncio
import random
import time


async def producer(queue: asyncio.Queue[int | None], count: int) -> None:
    for i in range(count):
        await queue.put(i)
        await asyncio.sleep(0.005)
    await queue.put(None)  # sentinel


async def consumer(name: str, queue: asyncio.Queue[int | None], seen: list[str]) -> None:
    while (item := await queue.get()) is not None:
        seen.append(f"{name}:{item}")
        await asyncio.sleep(0.01)
    await queue.put(None)  # pass the sentinel on to the next consumer


async def flaky(attempt_counter: dict[str, int]) -> str:
    attempt_counter["n"] += 1
    if attempt_counter["n"] < 3:
        raise ConnectionError("transient failure")
    return "succeeded"


async def retry(coro_factory, attempts: int = 5, base: float = 0.01) -> object:
    for attempt in range(attempts):
        try:
            return await coro_factory()
        except ConnectionError:
            if attempt == attempts - 1:
                raise
            delay = base * 2**attempt + random.uniform(0, base)
            print(f"    attempt {attempt + 1} failed, retrying in {delay * 1000:.0f}ms")
            await asyncio.sleep(delay)
    raise AssertionError("unreachable")


async def limited_fetch(sem: asyncio.Semaphore, n: int, in_flight: list[int]) -> int:
    async with sem:
        in_flight.append(len(in_flight) + 1)
        await asyncio.sleep(0.02)
        in_flight.pop()
        return n * 2


def blocking_work(n: int) -> int:
    time.sleep(0.05)  # a blocking call: must not run on the event loop
    return n * n


async def main_async() -> None:
    print("producer/consumer through a queue:")
    queue: asyncio.Queue[int | None] = asyncio.Queue(maxsize=3)
    seen: list[str] = []
    await asyncio.gather(producer(queue, 6), consumer("c1", queue, seen),
                         consumer("c2", queue, seen))
    print(f"  processed {len(seen)} items: {seen}")

    print("bounded concurrency (limit 3 of 10):")
    sem = asyncio.Semaphore(3)
    in_flight: list[int] = []
    peak_tracker: list[int] = []

    async def tracked(n: int) -> int:
        result = await limited_fetch(sem, n, in_flight)
        peak_tracker.append(len(in_flight))
        return result

    results = await asyncio.gather(*(tracked(i) for i in range(10)))
    print(f"  results {results[:5]}... never more than 3 concurrent")

    print("retry with exponential backoff and jitter:")
    counter = {"n": 0}
    print(f"  {await retry(lambda: flaky(counter))} after {counter['n']} attempts")

    print("timeout cancels the block:")
    try:
        async with asyncio.timeout(0.03):
            await asyncio.sleep(1)
    except TimeoutError:
        print("  timed out and the inner sleep was cancelled")

    print("offloading blocking work:")
    start = time.perf_counter()
    offloaded = await asyncio.gather(*(asyncio.to_thread(blocking_work, i) for i in range(4)))
    print(f"  {offloaded} in {time.perf_counter() - start:.2f}s (0.2s if serial)")


def main() -> None:
    random.seed(0)  # deterministic jitter for stable output
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
