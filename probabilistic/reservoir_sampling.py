"""Reservoir sampling: a uniform sample from a stream of unknown length.

You are handed items one at a time, you cannot store them all, and you do not
know how many are coming. You still want k of them, each chosen with equal
probability. Algorithm R does it in O(1) extra space beyond the sample itself
and one pass over the data.

Keep the first k items. For the i-th item after that, counting from zero, pick a
random index j in [0, i]. If j lands inside the reservoir, item i replaces the
one at j; otherwise item i is discarded. That is the whole algorithm.

The proof is a short induction. Item i enters with probability k/(i+1), and each
item already held survives a given step with probability 1 - k/(i+1) * 1/k, so
after n items every item has probability exactly k/n of being in the reservoir.
The intuition worth carrying away is that later items get rarer chances to
enter, which precisely compensates for the many chances earlier items have had
to be evicted.

Cost is O(n) time and O(k) space. The empirical check in main seeds the RNG so
the counts printed are stable across runs.
"""

import random
from typing import Iterable, TypeVar

T = TypeVar("T")


def reservoir_sample(stream: Iterable[T], k: int,
                     rng: random.Random | None = None) -> list[T]:
    """k items chosen uniformly from stream; fewer if the stream is shorter."""
    if k <= 0:
        return []
    r = rng or random.Random()
    reservoir: list[T] = []
    for i, item in enumerate(stream):
        if i < k:
            reservoir.append(item)
            continue
        # Item i is kept with probability k/(i+1); that is exactly j < k.
        j = r.randint(0, i)
        if j < k:
            reservoir[j] = item
    return reservoir


def uniformity_check(population: int, k: int, trials: int,
                     seed: int = 12345) -> dict[int, int]:
    """Count how often each item is sampled; ideal count is trials * k / n."""
    rng = random.Random(seed)
    counts = {i: 0 for i in range(population)}
    for _ in range(trials):
        for item in reservoir_sample(range(population), k, rng):
            counts[item] += 1
    return counts


def main() -> None:
    rng = random.Random(2024)
    print(f"3 of 0..19:      {reservoir_sample(range(20), 3, rng)}")
    print(f"3 of 0..19 again:{reservoir_sample(range(20), 3, rng)}")

    # A generator of unknown length works just as well as a list.
    def words() -> Iterable[str]:
        yield from "alpha beta gamma delta epsilon zeta eta theta".split()

    print(f"2 words: {reservoir_sample(words(), 2, rng)}")

    print(f"k larger than stream: {reservoir_sample([1, 2], 5, rng)}")
    print(f"k equals stream:      {reservoir_sample([1, 2, 3], 3, rng)}")
    print(f"empty stream:         {reservoir_sample([], 3, rng)}")
    print(f"k = 0:                {reservoir_sample(range(10), 0, rng)}")
    print(f"k negative:           {reservoir_sample(range(10), -1, rng)}")

    population, k, trials = 10, 3, 30000
    counts = uniformity_check(population, k, trials)
    expected = trials * k / population
    print(f"uniformity over {trials} trials, k={k}, n={population}")
    print(f"  expected count per item: {expected:.0f}")
    for item in range(population):
        deviation = (counts[item] - expected) / expected * 100
        print(f"  item {item}: {counts[item]:>6}  ({deviation:+.2f}%)")
    worst = max(abs(counts[i] - expected) / expected for i in range(population))
    print(f"  worst deviation: {worst * 100:.2f}%")


if __name__ == "__main__":
    main()
