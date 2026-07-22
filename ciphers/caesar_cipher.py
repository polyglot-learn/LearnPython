"""Caesar cipher: shift every letter forward by a fixed amount.

Named for Julius Caesar, who reportedly shifted by three. Encryption maps each
letter to the one k places later in the alphabet, wrapping past Z back to A;
decryption shifts by -k. Non-letters pass through untouched, which is itself a
weakness because it preserves word shape and punctuation.

This is a historical toy, not security. There are only 25 useful keys, so a
computer breaks it instantly by trying all of them, and the winner can be picked
automatically by scoring each candidate against English letter frequencies.
Never use this, or anything in this directory, to protect real data. For
integrity use hashlib and hmac from the standard library; for actual encryption
use a reviewed library such as cryptography or PyNaCl, never a hand-rolled one.

Encryption and decryption are O(n); brute force is O(25n) and its frequency
scoring is what turns a list of 25 guesses into one answer.
"""

ALPHABET_SIZE = 26

# Relative frequency of each letter in ordinary English text, A through Z.
ENGLISH_FREQ = [
    8.17, 1.49, 2.78, 4.25, 12.70, 2.23, 2.02, 6.09, 6.97, 0.15, 0.77, 4.03,
    2.41, 6.75, 7.51, 1.93, 0.10, 5.99, 6.33, 9.06, 2.76, 0.98, 2.36, 0.15,
    1.97, 0.07,
]


def shift_char(ch: str, key: int) -> str:
    if "a" <= ch <= "z":
        base = ord("a")
    elif "A" <= ch <= "Z":
        base = ord("A")
    else:
        return ch  # digits, spaces and punctuation are left as they are
    return chr(base + (ord(ch) - base + key) % ALPHABET_SIZE)


def encrypt(text: str, key: int) -> str:
    return "".join(shift_char(c, key) for c in text)


def decrypt(text: str, key: int) -> str:
    return encrypt(text, -key)


def english_score(text: str) -> float:
    """Chi-squared-style fit against English letter frequencies; lower is better."""
    counts = [0] * ALPHABET_SIZE
    total = 0
    for ch in text.lower():
        if "a" <= ch <= "z":
            counts[ord(ch) - ord("a")] += 1
            total += 1
    if total == 0:
        return float("inf")
    score = 0.0
    for i in range(ALPHABET_SIZE):
        expected = ENGLISH_FREQ[i] * total / 100.0
        score += (counts[i] - expected) ** 2 / max(expected, 1e-9)
    return score


def brute_force(text: str) -> list[tuple[int, str]]:
    """All 26 shifts, best English fit first."""
    candidates = [(k, decrypt(text, k)) for k in range(ALPHABET_SIZE)]
    return sorted(candidates, key=lambda kv: english_score(kv[1]))


def crack(text: str) -> tuple[int, str]:
    return brute_force(text)[0]


def main() -> None:
    message = "Attack at dawn, bring the ninth legion!"
    secret = encrypt(message, 3)
    print(f"plaintext:  {message}")
    print(f"key 3:      {secret}")
    print(f"decrypted:  {decrypt(secret, 3)}")
    print(f"round trip ok: {decrypt(secret, 3) == message}")

    print(f"key 0 is a no-op:      {encrypt(message, 0) == message}")
    print(f"key 26 wraps to a no-op: {encrypt(message, 26) == message}")
    print(f"key -3 equals key 23:  {encrypt(message, -3) == encrypt(message, 23)}")
    print(f"empty string:          {encrypt('', 5)!r}")
    print(f"digits untouched:      {encrypt('abc 123 xyz!', 3)}")

    print("top three brute-force guesses")
    for key, guess in brute_force(secret)[:3]:
        print(f"  key {key:>2}: {guess}")

    found_key, found_text = crack(secret)
    print(f"cracked with no key given: key={found_key} text={found_text}")

    # Frequency scoring needs enough text; a very short message misleads it.
    tiny = encrypt("hi", 7)
    print(f"short text is unreliable: {crack(tiny)}")


if __name__ == "__main__":
    main()
