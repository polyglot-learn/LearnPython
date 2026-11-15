"""dp_kit: classic DP problems that return the solution, plus a memoize decorator.

    >>> from dynamic_programming.dp_kit import edit_distance, coin_change
    >>> edit_distance("kitten", "sitting")
    3
    >>> coin_change([1, 5, 10, 25], 63)
    [25, 25, 10, 1, 1, 1]
"""

from .memo import memoize
from .problems import coin_change, count_paths, edit_distance, knapsack, lcs, lis

__all__ = ["memoize", "knapsack", "lcs", "edit_distance", "coin_change", "lis", "count_paths"]
