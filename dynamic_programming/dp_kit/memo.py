"""A tiny memoize decorator that shows what caching does to a recursion."""

import functools
from collections.abc import Callable
from typing import Any


def memoize(func: Callable) -> Callable:
    """Cache by positional arguments; ``wrapper.calls`` counts real executions."""
    cache: dict[tuple, Any] = {}

    @functools.wraps(func)
    def wrapper(*args: Any) -> Any:
        if args not in cache:
            wrapper.calls += 1
            cache[args] = func(*args)
        return cache[args]

    wrapper.calls = 0
    wrapper.cache = cache
    return wrapper
