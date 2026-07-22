"""Tasks, cancellation, and bounding concurrency.

`asyncio.create_task` schedules a coroutine to run *now*, alongside the
caller, and hands back a handle. The handle lets you await the result later,
cancel it, or check whether it finished.

Cancellation is delivered as a `CancelledError` raised inside the task at its
next await point. A task that never awaits can never be cancelled — and any
cleanup you need must live in a `finally` block.

`asyncio.Semaphore` is the standard way to cap how many tasks run at once.
"""

import asyncio


async def worker(name: str, seconds: float) -> str:
    try:
        await asyncio.sleep(seconds)
        return f"{name} finished"
    except asyncio.CancelledError:
        print(f"  {name} was cancelled")
        raise  # re-raise: swallowing it breaks structured cancellation
    finally:
        print(f"  {name} cleaned up")


async def limited(sem: asyncio.Semaphore, name: str) -> str:
    async with sem:  # at most N holders at a time
        print(f"  {name} acquired the semaphore")
        await asyncio.sleep(0.05)
        return name


async def main_async() -> None:
    print("create_task runs work in the background:")
    task = asyncio.create_task(worker("bg", 0.05))
    print(f"  task done yet? {task.done()}")
    print(f"  awaited: {await task}")

    print("cancellation:")
    slow = asyncio.create_task(worker("slow", 10))
    await asyncio.sleep(0.01)  # let it start
    slow.cancel()
    try:
        await slow
    except asyncio.CancelledError:
        print(f"  cancelled: {slow.cancelled()}")

    print("bounded concurrency (2 at a time, 5 jobs):")
    sem = asyncio.Semaphore(2)
    names = [f"job{i}" for i in range(5)]
    results = await asyncio.gather(*(limited(sem, n) for n in names))
    print(f"  {results}")

    print("gather(return_exceptions=True) keeps one failure from killing the rest:")

    async def boom() -> str:
        raise RuntimeError("kaboom")

    mixed = await asyncio.gather(worker("ok", 0.01), boom(), return_exceptions=True)
    print(f"  {mixed}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
