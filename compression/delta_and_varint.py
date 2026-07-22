"""Delta coding plus LEB128 varints: how sorted id lists get small.

A sorted list of ids has huge values but tiny differences. Store the first value
and then each gap, and the numbers to encode shrink from millions to tens. That
alone saves nothing while every number still occupies four or eight fixed bytes,
so the second half matters just as much: a variable-length integer format that
spends one byte on small numbers.

LEB128 writes seven bits of the value per byte, with the high bit set on every
byte except the last. So 0-127 costs one byte, up to 16383 costs two, and so on.
Deltas can be negative once a list is unsorted, so zigzag mapping interleaves
signs (0, -1, 1, -2, ...) into unsigned values before encoding, keeping small
negatives cheap.

Both steps are exactly reversible, and both can expand: a list of large random
gaps encodes to more bytes than a packed fixed-width array would need.
"""


def delta_encode(values: list[int]) -> list[int]:
    if not values:
        return []
    return [values[0]] + [b - a for a, b in zip(values, values[1:])]


def delta_decode(deltas: list[int]) -> list[int]:
    out: list[int] = []
    total = 0
    for d in deltas:
        total += d
        out.append(total)
    return out


def zigzag(n: int) -> int:
    """Map ..., -2, -1, 0, 1, 2 ... onto 3, 1, 0, 2, 4 ... so |small| stays small."""
    return (n << 1) ^ -1 if n < 0 else n << 1


def unzigzag(n: int) -> int:
    return (n >> 1) ^ -(n & 1)


def encode_varint(n: int) -> bytes:
    """LEB128 over a non-negative int: 7 payload bits per byte, MSB = continue."""
    if n < 0:
        raise ValueError("apply zigzag first")
    out = bytearray()
    while True:
        byte = n & 0x7F
        n >>= 7
        out.append(byte | 0x80 if n else byte)
        if not n:
            return bytes(out)


def decode_varints(data: bytes) -> list[int]:
    out: list[int] = []
    value = shift = 0
    started = False
    for byte in data:
        value |= (byte & 0x7F) << shift
        shift += 7
        started = True
        if not byte & 0x80:
            out.append(value)
            value = shift = 0
            started = False
    if started:
        raise ValueError("truncated varint: last byte still had the continue bit")
    return out


def pack(values: list[int]) -> bytes:
    deltas = delta_encode(values)
    return b"".join(encode_varint(zigzag(d)) for d in deltas)


def unpack(data: bytes) -> list[int]:
    return delta_decode([unzigzag(n) for n in decode_varints(data)])


def report(values: list[int], data: bytes) -> str:
    if not values:
        return "n/a (empty input)"
    before = len(values) * 4  # a plain uint32 array
    after = len(data)
    return f"{before} B -> {after} B ({after / before:.2f}x)"


def main() -> None:
    samples: list[list[int]] = [
        [],
        [1_000_000, 1_000_003, 1_000_011, 1_000_012, 1_000_400],
        [5, 3, 9, 1, 100, -40],  # unsorted and negative: zigzag earns its keep
        [i * 900_000_007 for i in range(1, 6)],  # gaps past 2**28: varints expand
    ]
    for values in samples:
        data = pack(values)
        back = unpack(data)
        print(f"input     : {values}")
        print(f"deltas    : {delta_encode(values)}")
        print(f"packed    : {data.hex()}")
        print(f"round-trip: {back == values}")
        print(f"size      : {report(values, data)}")
        print()

    # A realistic ascending id list, the case this pairing was designed for.
    ids = list(range(4_000_000, 4_000_000 + 2000, 3))
    data = pack(ids)
    print(f"{len(ids)} ids: {report(ids, data)}")
    print(f"round-trip: {unpack(data) == ids}")
    print(f"varint of 127 -> {encode_varint(127).hex()}, "
          f"128 -> {encode_varint(128).hex()}")


if __name__ == "__main__":
    main()
