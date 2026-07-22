"""Subset sum: is there a subset of these numbers adding up to the target?

The decision at each index is binary — take the number or skip it — so the raw
search tree has 2^n leaves. Backtracking beats that by refusing to descend into
branches that provably cannot reach the target.

Three prunings do most of the work, and they need the input sorted. Keep a
running suffix sum of everything still available: if the remaining need exceeds
that, no completion exists, so return. If the remaining need is zero, record a
hit without touching the rest. And with all-positive inputs sorted ascending,
once the current number alone overshoots the need, every later number does too,
so the loop can break rather than continue.

Deciding takes exponential time in the worst case (the problem is NP-complete),
though a dynamic-programming table solves it in O(n * target) when the target is
a modest integer. Enumerating all subsets is unavoidably output-bound, since
there can be exponentially many answers.
"""

from itertools import accumulate


def _checked(numbers: list[int]) -> list[int]:
    """Sorted ascending. The prunings below assume non-negative inputs."""
    if any(x < 0 for x in numbers):
        raise ValueError("negative values break the suffix-sum pruning")
    return sorted(numbers)


def can_sum(numbers: list[int], target: int) -> bool:
    nums = _checked(numbers)
    # suffix[i] is the sum of nums[i:]; the most any tail can still contribute.
    suffix = list(accumulate(reversed(nums)))[::-1] + [0]

    def recurse(i: int, need: int) -> bool:
        if need == 0:
            return True
        if i == len(nums) or need < 0 or need > suffix[i]:
            return False
        return recurse(i + 1, need - nums[i]) or recurse(i + 1, need)

    return recurse(0, target)


def all_subsets_summing(numbers: list[int], target: int) -> list[list[int]]:
    nums = _checked(numbers)
    suffix = list(accumulate(reversed(nums)))[::-1] + [0]
    found: list[list[int]] = []
    chosen: list[int] = []

    def recurse(i: int, need: int) -> None:
        if need == 0:
            found.append(list(chosen))
            return
        if i == len(nums) or need < 0 or need > suffix[i]:
            return
        for j in range(i, len(nums)):
            if nums[j] > need:
                break  # sorted ascending: no later number fits either
            if need > suffix[j]:
                break  # even taking everything left falls short
            chosen.append(nums[j])
            recurse(j + 1, need - nums[j])
            chosen.pop()

    recurse(0, target)
    return found


def can_sum_dp(numbers: list[int], target: int) -> bool:
    """O(n * target) table, valid for non-negative inputs and target."""
    if target < 0 or any(x < 0 for x in numbers):
        raise ValueError("dp version needs non-negative values")
    reachable = 1  # bit t set means "sum t is achievable"
    for x in numbers:
        reachable |= reachable << x
    return bool(reachable >> target & 1)


def count_calls(numbers: list[int], target: int) -> tuple[bool, int]:
    """Same search without pruning, to show what the pruning is worth."""
    nums = sorted(numbers)
    calls = 0

    def recurse(i: int, need: int) -> bool:
        nonlocal calls
        calls += 1
        if need == 0:
            return True
        if i == len(nums):
            return False
        return recurse(i + 1, need - nums[i]) or recurse(i + 1, need)

    return recurse(0, target), calls


def main() -> None:
    nums = [3, 34, 4, 12, 5, 2]
    for target in (9, 30, 60, 0, 1):
        print(f"can_sum({nums}, {target}): {can_sum(nums, target)}")

    print(f"subsets summing to 9:  {all_subsets_summing(nums, 9)}")
    print(f"subsets summing to 10: {all_subsets_summing(nums, 10)}")
    print(f"subsets summing to 0:  {all_subsets_summing(nums, 0)}")
    print(f"subsets summing to 1:  {all_subsets_summing(nums, 1)}")

    # Subsets are enumerated by index, so equal values give repeated answers.
    dupes = [1, 1, 2, 2]
    print(f"duplicates, target 3: {all_subsets_summing(dupes, 3)}")

    print(f"empty list, target 0: {can_sum([], 0)}")
    print(f"empty list, target 5: {can_sum([], 5)}")

    agree = all(
        can_sum(nums, t) == can_sum_dp(nums, t) for t in range(0, 61)
    )
    print(f"backtracking and dp agree for targets 0..60: {agree}")

    # Pruning shows up as a much smaller search tree on an unreachable target.
    hard = list(range(1, 21))
    print(f"unpruned calls for an impossible target: {count_calls(hard, 1000)}")
    print(f"pruned result for the same target: {can_sum(hard, 1000)}")


if __name__ == "__main__":
    main()
