"""Minimum meeting rooms: how many intervals overlap at the worst moment.

Given meetings with start and end times, the fewest rooms needed equals the
maximum number of meetings in progress simultaneously. That equivalence is the
whole insight: any instant with k concurrent meetings forces at least k rooms,
and processing meetings in start order never needs more than that maximum.

The implementation processes meetings sorted by start time and keeps a min-heap
of the end times of the rooms currently in use. For each meeting, if the room
that frees up earliest is already free by its start, reuse that room; otherwise
open a new one. The heap size at the end is the answer, and its peak is the
answer during the sweep.

Cost is O(n log n) for the sort plus O(n log n) of heap operations, and O(n)
space. The same count also falls out of a sweep line over sorted start and end
events, which is the variant shown for comparison; the heap version has the
advantage of also telling you which meeting went in which room.
"""

import heapq

Meeting = tuple[str, int, int]  # name, start, end


def min_rooms(meetings: list[Meeting]) -> int:
    ends: list[int] = []
    for _, start, end in sorted(meetings, key=lambda m: m[1]):
        if ends and ends[0] <= start:
            heapq.heapreplace(ends, end)  # reuse the earliest-freeing room
        else:
            heapq.heappush(ends, end)
    return len(ends)


def assign_rooms(meetings: list[Meeting]) -> dict[int, list[Meeting]]:
    """Same sweep, but records the assignment. Heap holds (end time, room id)."""
    free: list[tuple[int, int]] = []
    rooms: dict[int, list[Meeting]] = {}
    for meeting in sorted(meetings, key=lambda m: m[1]):
        _, start, end = meeting
        if free and free[0][0] <= start:
            _, room = heapq.heappop(free)
        else:
            room = len(rooms)
        rooms.setdefault(room, []).append(meeting)
        heapq.heappush(free, (end, room))
    return rooms


def max_concurrent_sweep(meetings: list[Meeting]) -> int:
    """Sweep line: +1 at every start, -1 at every end, ends processed first."""
    events = sorted(
        [(m[1], 1) for m in meetings] + [(m[2], -1) for m in meetings]
    )
    current = peak = 0
    for _, delta in events:
        current += delta
        peak = max(peak, current)
    return peak


def main() -> None:
    meetings: list[Meeting] = [
        ("standup", 0, 30), ("design", 5, 10), ("1:1", 15, 20),
        ("review", 25, 40), ("retro", 35, 50), ("planning", 45, 60),
    ]
    print(f"rooms needed: {min_rooms(meetings)}")
    print(f"sweep-line agrees: {max_concurrent_sweep(meetings) == min_rooms(meetings)}")

    for room, booked in sorted(assign_rooms(meetings).items()):
        slots = ", ".join(f"{n} [{s},{e})" for n, s, e in booked)
        print(f"  room {room}: {slots}")

    print(f"\nempty: {min_rooms([])}")
    print(f"single: {min_rooms([('solo', 0, 1)])}")

    touching: list[Meeting] = [("a", 0, 5), ("b", 5, 10), ("c", 10, 15)]
    print(f"back-to-back (end == next start): {min_rooms(touching)} room")

    nested: list[Meeting] = [("a", 0, 100), ("b", 10, 20), ("c", 12, 15)]
    print(f"fully nested: {min_rooms(nested)} rooms")

    identical: list[Meeting] = [(f"m{i}", 0, 10) for i in range(5)]
    print(f"five identical meetings: {min_rooms(identical)} rooms")

    # Many short meetings in sequence still need just one room.
    chain: list[Meeting] = [(f"c{i}", i, i + 1) for i in range(1000)]
    print(f"1000 back-to-back meetings: {min_rooms(chain)} room")


if __name__ == "__main__":
    main()
