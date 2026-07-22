"""`contextvars` — per-task state that survives await points.

A module global is shared by everything. `threading.local()` is per *thread*,
which breaks under asyncio because thousands of tasks share one thread.
`ContextVar` is per *context*: each asyncio task gets a copy on creation, so a
request id set at the top of a handler stays correct across every await inside
it, and never leaks into a sibling task.

`set()` returns a Token; `reset(token)` restores the previous value, which is
what makes it safe inside a context manager.
"""

import asyncio
import contextvars
import threading

request_id: contextvars.ContextVar[str] = contextvars.ContextVar(
    "request_id", default="-"
)

thread_state = threading.local()


def log(message: str) -> None:
    print(f"  [{request_id.get()}] {message}")


async def handle(rid: str, delay: float) -> None:
    token = request_id.set(rid)
    try:
        log("started")
        await asyncio.sleep(delay)  # other tasks run here, with their own value
        log("finished")
    finally:
        request_id.reset(token)


async def main_async() -> None:
    print("interleaved tasks keep their own request id:")
    await asyncio.gather(handle("req-1", 0.03), handle("req-2", 0.01))

    log("back outside any task (default value)")

    # A snapshot of the current context can be run elsewhere.
    request_id.set("snapshot")
    ctx = contextvars.copy_context()
    request_id.set("changed-after-copy")
    ctx.run(log, "running inside the copied context")
    log("current context")


def thread_demo() -> None:
    def worker(name: str) -> None:
        thread_state.name = name  # invisible to other threads
        print(f"  thread {name} sees {thread_state.name}")

    threads = [threading.Thread(target=worker, args=(f"t{i}",)) for i in range(3)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()
    print(f"  main thread has a name attribute: {hasattr(thread_state, 'name')}")


def main() -> None:
    asyncio.run(main_async())
    print("threading.local for comparison:")
    thread_demo()


if __name__ == "__main__":
    main()
