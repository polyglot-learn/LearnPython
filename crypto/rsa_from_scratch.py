"""RSA from scratch — the textbook algorithm, for learning only.

RSA rests on one asymmetry: multiplying two large primes is easy, factoring
their product is not. Pick primes p and q, let n = p*q and phi = (p-1)(q-1);
choose a public exponent e coprime to phi, and the private exponent d is its
modular inverse. Then (m^e)^d = m (mod n) by Euler's theorem, so encrypting
with (e, n) is undone only by the holder of d.

This file uses small primes and raw ("textbook") RSA with no padding, which is
insecure in every real sense — deterministic, malleable, and vulnerable to a
dozen attacks. Never use it for anything real; use the `cryptography` library,
which implements RSA-OAEP and constant-time operations.
"""

import secrets
from math import gcd


def is_probable_prime(n: int, rounds: int = 20) -> bool:
    if n < 2:
        return False
    for p in (2, 3, 5, 7, 11, 13, 17, 19, 23, 29, 31, 37):
        if n % p == 0:
            return n == p
    d, r = n - 1, 0
    while d % 2 == 0:
        d //= 2
        r += 1
    for _ in range(rounds):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x in (1, n - 1):
            continue
        for _ in range(r - 1):
            x = x * x % n
            if x == n - 1:
                break
        else:
            return False
    return True


def generate_prime(bits: int) -> int:
    while True:
        candidate = secrets.randbits(bits) | (1 << (bits - 1)) | 1  # top and bottom bit set
        if is_probable_prime(candidate):
            return candidate


def generate_keypair(bits: int = 256) -> tuple[tuple[int, int], tuple[int, int]]:
    p = generate_prime(bits)
    q = generate_prime(bits)
    while q == p:
        q = generate_prime(bits)
    n = p * q
    phi = (p - 1) * (q - 1)
    e = 65537
    while gcd(e, phi) != 1:
        e += 2
    d = pow(e, -1, phi)  # modular inverse (Python 3.8+)
    return (e, n), (d, n)


def encrypt(message: int, public: tuple[int, int]) -> int:
    e, n = public
    return pow(message, e, n)


def decrypt(cipher: int, private: tuple[int, int]) -> int:
    d, n = private
    return pow(cipher, d, n)


def sign(message: int, private: tuple[int, int]) -> int:
    d, n = private
    return pow(message, d, n)  # signing is decryption with the private key


def verify(message: int, signature: int, public: tuple[int, int]) -> bool:
    e, n = public
    return pow(signature, e, n) == message


def main() -> None:
    public, private = generate_keypair(bits=256)
    e, n = public
    print(f"public exponent e = {e}")
    print(f"modulus n has {n.bit_length()} bits")

    message = 42
    cipher = encrypt(message, public)
    print(f"encrypt({message}) -> {str(cipher)[:40]}...")
    print(f"decrypt(cipher) -> {decrypt(cipher, private)}")
    print(f"round-trip: {decrypt(encrypt(message, public), private) == message}")

    # Larger message, still below n.
    big = int.from_bytes(b"hello", "big")
    print(f"'hello' as int {big} round-trips: {decrypt(encrypt(big, public), private) == big}")

    # Signatures: private signs, public verifies.
    signature = sign(big, private)
    print(f"valid signature verifies: {verify(big, signature, public)}")
    print(f"tampered message rejected: {verify(big + 1, signature, public)}")

    # The insecurity of textbook RSA: it is deterministic and multiplicative.
    print("textbook RSA is deterministic — same plaintext, same ciphertext:")
    print(f"  {encrypt(42, public) == encrypt(42, public)}")
    print("and malleable: E(a)*E(b) mod n = E(a*b), which real padding prevents")
    ea, eb = encrypt(3, public), encrypt(4, public)
    print(f"  E(3)*E(4) decrypts to {decrypt(ea * eb % n, private)} (= 12)")


if __name__ == "__main__":
    main()
