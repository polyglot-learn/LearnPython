"""Async generators and `async for` — streaming values that arrive over time.

An `async def` containing `yield` is an async generator. Consume it with
`async for`, which awaits between items. This is the shape of anything that
produces data gradually: paginated APIs, websocket frames, tailing a log.

`async with` is the asynchronous context manager, for resources whose setup or
teardown must await (a connection, a pool, a lock).
"""

import asyncio
from collections.abc import AsyncIterator


async def ticker(count: int, interval: float) -> AsyncIterator[int]:
    for i in range(count):
        await asyncio.sleep(interval)
        yield i


async def paginated(pages: int) -> AsyncIterator[list[str]]:
    """Pretend each page costs a round trip."""
    for page in range(pages):
        await asyncio.sleep(0.02)
        yield [f"item-{page}-{n}" for n in range(2)]


class Connection:
    async def __aenter__(self) -> "Connection":
        await asyncio.sleep(0.01)
        print("  connection opened")
        return self

    async def __aexit__(self, *exc_info: object) -> None:
        await asyncio.sleep(0.01)
        print("  connection closed")

    async def query(self, sql: str) -> str:
        await asyncio.sleep(0.01)
        return f"rows for {sql!r}"


async def main_async() -> None:
    print("async for over a ticker:")
    async for tick in ticker(3, 0.05):
        print(f"  tick {tick}")

    print("flattening pages as they arrive:")
    all_items = [item async for page in paginated(3) for item in page]
    print(f"  {all_items}")

    print("async with:")
    async with Connection() as conn:
        print(f"  {await conn.query('select 1')}")

    # An async generator can be consumed manually too.
    gen = ticker(2, 0.01)
    print(f"manual anext: {await anext(gen)}, {await anext(gen)}")
    print(f"exhausted -> {await anext(gen, 'stop')}")


def main() -> None:
    asyncio.run(main_async())


if __name__ == "__main__":
    main()
