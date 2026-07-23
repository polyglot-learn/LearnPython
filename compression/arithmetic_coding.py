"""Arithmetic coding: encode a whole message as a single fraction in [0, 1).

Huffman coding must spend a whole number of bits per symbol, so it wastes up to
a bit each time and cannot beat one bit per symbol however predictable the
source. Arithmetic coding sidesteps that by encoding the entire message as one
number. Start with the interval [0, 1); each symbol narrows it to the
sub-interval its probability occupies. The final interval is so small that any
number inside it identifies the exact symbol sequence — and its width equals the
message probability, so the bit length approaches the Shannon entropy.

This uses integer range coding with E1/E2/E3 renormalisation, the practical form
that avoids floating-point drift by rescaling the interval and emitting bits as
the top bits of the bounds settle. Encode and decode are exact inverses.

Near-optimal compression; O(n) in the message length.
"""

from collections import Counter

PRECISION = 32
FULL = 1 << PRECISION
HALF = FULL >> 1
QUARTER = FULL >> 2
MASK = FULL - 1


def _cumulative(freqs: dict[str, int]) -> tuple[dict[str, tuple[int, int]], int]:
    total = sum(freqs.values())
    table: dict[str, tuple[int, int]] = {}
    low = 0
    for symbol in sorted(freqs):
        table[symbol] = (low, low + freqs[symbol])
        low += freqs[symbol]
    return table, total


def encode(message: str, freqs: dict[str, int]) -> tuple[list[int], int]:
    table, total = _cumulative(freqs)
    low, high = 0, MASK
    pending = 0
    bits: list[int] = []

    def emit(bit: int) -> None:
        bits.append(bit)
        bits.extend([bit ^ 1] * pending)  # deferred opposite bits (E3 case)

    for symbol in message:
        span = high - low + 1
        sym_low, sym_high = table[symbol]
        high = low + span * sym_high // total - 1
        low = low + span * sym_low // total
        while True:
            if high < HALF:
                emit(0)
                pending = 0
            elif low >= HALF:
                emit(1)
                pending = 0
                low -= HALF
                high -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:  # E3: straddling the middle
                pending += 1
                low -= QUARTER
                high -= QUARTER
            else:
                break
            low <<= 1
            high = (high << 1) | 1

    pending += 1  # flush
    emit(0 if low < QUARTER else 1)
    return bits, len(message)


def decode(bits: list[int], length: int, freqs: dict[str, int]) -> str:
    table, total = _cumulative(freqs)
    inverse = {v: k for k, v in table.items()}
    low, high = 0, MASK
    stream = iter(bits)
    value = 0
    for _ in range(PRECISION):
        value = (value << 1) | next(stream, 0)

    out: list[str] = []
    for _ in range(length):
        span = high - low + 1
        # Which symbol interval does the current value fall in?
        scaled = ((value - low + 1) * total - 1) // span
        symbol = next(s for s, (lo, hi) in table.items() if lo <= scaled < hi)
        out.append(symbol)
        sym_low, sym_high = table[symbol]
        high = low + span * sym_high // total - 1
        low = low + span * sym_low // total
        while True:
            if high < HALF:
                pass
            elif low >= HALF:
                low -= HALF
                high -= HALF
                value -= HALF
            elif low >= QUARTER and high < 3 * QUARTER:
                low -= QUARTER
                high -= QUARTER
                value -= QUARTER
            else:
                break
            low <<= 1
            high = (high << 1) | 1
            value = (value << 1) | next(stream, 0)
    return "".join(out)


def main() -> None:
    import math

    for message in ("hello arithmetic coding", "aaaaaaaaaabaaaaaaaaaa", "abc", "x"):
        freqs = dict(Counter(message))
        bits, length = encode(message, freqs)
        decoded = decode(bits, length, freqs)
        entropy = -sum(
            (c / len(message)) * math.log2(c / len(message)) for c in freqs.values()
        )
        preview = message if len(message) <= 24 else message[:24] + "..."
        print(f"  {preview!r:<30} {len(bits)} bits, "
              f"entropy floor {entropy * len(message):.1f}, round-trip {decoded == message}")

    # The skewed source is where arithmetic coding beats Huffman's 1-bit floor.
    skewed = "a" * 100 + "b"
    bits, length = encode(skewed, dict(Counter(skewed)))
    print(f"100 a's + 1 b: {len(bits)} bits total "
          f"({len(bits) / len(skewed):.3f} bits/symbol; Huffman needs >= 1)")

    print(f"empty-ish edge: single symbol round-trips: "
          f"{decode(*encode('z', {'z': 1}), {'z': 1}) == 'z'}")


if __name__ == "__main__":
    main()
