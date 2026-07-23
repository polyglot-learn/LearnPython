"""HMAC from scratch — why you cannot just prepend a key to a hash.

A message authentication code proves a message came from someone holding the
shared key and was not altered. The naive construction H(key || message) is
broken for Merkle-Damgard hashes like SHA-256: because those hashes process
data in blocks and expose their internal state as the output, an attacker can
"length-extend" a valid tag to authenticate a longer message they never saw.

HMAC fixes this with two nested hashes and two derived keys:
    HMAC(k, m) = H((k ^ opad) || H((k ^ ipad) || m))
The outer hash wraps the inner one, so the exposed state is never a usable
prefix. The ipad/opad constants just make the two derived keys differ.

This mirrors the standard byte for byte and matches Python's hmac module. In
real code, always use hmac.new and compare tags with hmac.compare_digest.
"""

import hashlib
import hmac

BLOCK_SIZE = 64  # SHA-256 processes 64-byte blocks


def hmac_sha256(key: bytes, message: bytes) -> bytes:
    # Keys longer than a block are hashed down; shorter ones are zero-padded.
    if len(key) > BLOCK_SIZE:
        key = hashlib.sha256(key).digest()
    key = key.ljust(BLOCK_SIZE, b"\x00")

    inner_pad = bytes(b ^ 0x36 for b in key)  # ipad
    outer_pad = bytes(b ^ 0x5C for b in key)  # opad

    inner = hashlib.sha256(inner_pad + message).digest()
    return hashlib.sha256(outer_pad + inner).digest()


def main() -> None:
    key = b"shared secret key"
    message = b"transfer $100 to Alice"

    mine = hmac_sha256(key, message)
    reference = hmac.new(key, message, hashlib.sha256).digest()
    print(f"my HMAC:        {mine.hex()[:32]}...")
    print(f"stdlib HMAC:    {reference.hex()[:32]}...")
    print(f"they match:     {mine == reference}")

    # Verification: constant-time comparison, never ==.
    tag = hmac_sha256(key, message)
    print(f"valid tag verifies: {hmac.compare_digest(tag, hmac_sha256(key, message))}")

    tampered = b"transfer $9000 to Mallory"
    print(f"tampered message rejected: "
          f"{not hmac.compare_digest(tag, hmac_sha256(key, tampered))}")
    print(f"wrong key rejected: "
          f"{not hmac.compare_digest(tag, hmac_sha256(b'wrong key', message))}")

    # Keys of every length are handled.
    for k in (b"", b"short", b"x" * 100):
        ok = hmac_sha256(k, message) == hmac.new(k, message, hashlib.sha256).digest()
        print(f"key of length {len(k):>3}: matches stdlib = {ok}")

    # Why not H(key || message)? A one-bit change anywhere flips the whole tag,
    # but the naive scheme is still forgeable by length extension — HMAC is not.
    print("naive H(key||message) is length-extendable; HMAC's nesting blocks it")

    # A single flipped bit in the message avalanches the tag.
    flipped = bytearray(message)
    flipped[0] ^= 1
    diff = sum(bin(a ^ b).count("1") for a, b in zip(tag, hmac_sha256(key, bytes(flipped))))
    print(f"one input bit flipped -> {diff} of 256 output bits changed (~half)")


if __name__ == "__main__":
    main()
