"""Bitwise operations in Python, where integers have no fixed width.

The five operators are and, or, xor, not and the two shifts. And clears bits,
or sets them, xor flips them conditionally and is its own inverse, and shifting
left by k multiplies by 2^k while shifting right by k floor-divides by it.

The unusual part is Python's model. Integers are arbitrary precision, and
negative numbers behave as if written in two's complement with an infinite run
of leading sign bits. So ~n is exactly -n - 1 for every n, -1 has every bit set,
and -1 >> 100 is still -1 because the sign bits never run out. There is no
overflow and no unsigned type, which means "the top bit" is not a thing until
you supply a width yourself.

That is what masking is for. Anding with (1 << width) - 1 fixes a working width
and gives the value the same bits a fixed-size machine word would hold, which
is how you emulate C-style unsigned arithmetic. int.bit_length() reports the
bits needed for the magnitude, ignoring the sign.
"""


def mask(width: int) -> int:
    """All-ones value of the given width: the standard way to bound an int."""
    return (1 << width) - 1


def to_unsigned(n: int, width: int = 32) -> int:
    """Reinterpret n as an unsigned value of `width` bits."""
    return n & mask(width)


def to_signed(n: int, width: int = 32) -> int:
    """Inverse of to_unsigned: sign-extend a width-bit pattern back to Python."""
    n &= mask(width)
    sign = 1 << (width - 1)
    return n - (1 << width) if n & sign else n


def bits(n: int, width: int = 8) -> str:
    return format(to_unsigned(n, width), f"0{width}b")


def get_bit(n: int, i: int) -> int:
    return n >> i & 1


def main() -> None:
    a, b = 0b1100, 0b1010
    print(f"a       = {bits(a)} ({a})")
    print(f"b       = {bits(b)} ({b})")
    print(f"a & b   = {bits(a & b)} ({a & b})   common bits")
    print(f"a | b   = {bits(a | b)} ({a | b})   either bit")
    print(f"a ^ b   = {bits(a ^ b)} ({a ^ b})    differing bits")
    print(f"a << 2  = {bits(a << 2)} ({a << 2})  multiply by 4")
    print(f"a >> 2  = {bits(a >> 2)} ({a >> 2})    floor-divide by 4")

    print(f"\n~12 = {~12}, and ~n == -n - 1 for all n: "
          f"{all(~n == -n - 1 for n in range(-50, 50))}")
    print(f"bin(-12) prints as {bin(-12)} — a sign, not a bit pattern")
    print(f"-12 in 8-bit two's complement: {bits(-12)}")
    print(f"-1 >> 100 = {-1 >> 100}  (sign bits never run out)")

    print(f"\nmask(8)  = {mask(8)} = {bin(mask(8))}")
    print(f"to_unsigned(-1, 8)  = {to_unsigned(-1, 8)}")
    print(f"to_unsigned(-1, 32) = {to_unsigned(-1, 32)}")
    print(f"to_signed(0xFF, 8)  = {to_signed(0xFF, 8)}")
    print(f"to_signed(0x7F, 8)  = {to_signed(0x7F, 8)}")
    round_trip = all(to_signed(to_unsigned(n, 8), 8) == n for n in range(-128, 128))
    print(f"8-bit round trip holds for -128..127: {round_trip}")

    # Shifting left never overflows, which is a real difference from C.
    print(f"\n1 << 200 has {(1 << 200).bit_length()} bits")
    print(f"(1 << 200) & mask(32) = {(1 << 200) & mask(32)}")

    print(f"\nbit_length(0)={(0).bit_length()}, bit_length(1)={(1).bit_length()}, "
          f"bit_length(255)={(255).bit_length()}, bit_length(-255)={(-255).bit_length()}")
    print(f"bits of 37 low to high: {[get_bit(37, i) for i in range(6)]}")

    # Common idioms, each one line.
    n = 0b1011_0100
    print(f"\nn                 = {bits(n)}")
    print(f"lowest set bit    = {bits(n & -n)}    (n & -n)")
    print(f"clear lowest set  = {bits(n & (n - 1))}    (n & (n-1))")
    print(f"set lowest zero   = {bits(n | (n + 1))}    (n | (n+1))")
    print(f"low 4 bits        = {bits(n & mask(4))}    (n & 0b1111)")
    print(f"is odd            = {bool(n & 1)}        (n & 1)")


if __name__ == "__main__":
    main()
