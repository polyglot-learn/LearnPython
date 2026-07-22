"""Merge overlapping intervals — sort by start, then extend or append.

After sorting by start, an interval overlaps the previous merged one exactly
when its start is <= the merged end. Merging is then a single sweep, and the
only decision per step is "extend the current interval or start a new one".

O(n log n) for the sort, O(n) for the sweep.
"""


def merge_intervals(intervals: list[tuple[int, int]]) -> list[tuple[int, int]]:
    if not intervals:
        return []
    merged: list[tuple[int, int]] = []
    for start, end in sorted(intervals):
        if merged and start <= merged[-1][1]:
            prev_start, prev_end = merged[-1]
            merged[-1] = (prev_start, max(prev_end, end))
        else:
            merged.append((start, end))
    return merged


def insert_interval(
    intervals: list[tuple[int, int]], new: tuple[int, int]
) -> list[tuple[int, int]]:
    """Insert into an already-sorted, non-overlapping list in O(n)."""
    out: list[tuple[int, int]] = []
    start, end = new
    i, n = 0, len(intervals)
    while i < n and intervals[i][1] < start:  # entirely before
        out.append(intervals[i])
        i += 1
    while i < n and intervals[i][0] <= end:  # overlapping
        start = min(start, intervals[i][0])
        end = max(end, intervals[i][1])
        i += 1
    out.append((start, end))
    out.extend(intervals[i:])
    return out


def max_overlap(intervals: list[tuple[int, int]]) -> int:
    """Peak concurrency, via a +1/-1 sweep over the endpoints."""
    events: list[tuple[int, int]] = []
    for start, end in intervals:
        events.append((start, 1))
        events.append((end, -1))  # ends before starts at the same coordinate
    events.sort()
    current = best = 0
    for _, delta in events:
        current += delta
        best = max(best, current)
    return best


def main() -> None:
    data = [(1, 3), (2, 6), (8, 10), (15, 18)]
    print(f"merged  = {merge_intervals(data)}")
    print(f"insert  = {insert_interval([(1, 3), (6, 9)], (2, 5))}")
    print(f"overlap = {max_overlap([(1, 5), (2, 6), (3, 4), (7, 8)])}")
    print(f"empty   = {merge_intervals([])}")


if __name__ == "__main__":
    main()
