"""Palindrome checks — three shapes of the same question.

`s == s[::-1]` is the idiomatic one-liner, but it allocates a reversed copy.
The two-pointer version runs in O(1) space and is the one to reach for when
the input is large or the comparison rule is non-trivial (skipping
punctuation, folding case, ignoring diacritics).

O(n) time in every version.
"""

import unicodedata


def is_palindrome(text: str) -> bool:
    return text == text[::-1]


def is_palindrome_two_pointer(text: str) -> bool:
    lo, hi = 0, len(text) - 1
    while lo < hi:
        if text[lo] != text[hi]:
            return False
        lo += 1
        hi -= 1
    return True


def is_palindrome_relaxed(text: str) -> bool:
    """Ignore case and anything that is not alphanumeric."""
    lo, hi = 0, len(text) - 1
    while lo < hi:
        while lo < hi and not text[lo].isalnum():
            lo += 1
        while lo < hi and not text[hi].isalnum():
            hi -= 1
        if text[lo].casefold() != text[hi].casefold():
            return False
        lo += 1
        hi -= 1
    return True


def is_palindrome_unicode(text: str) -> bool:
    """Normalise first: 'é' can be one code point or two."""
    normalised = unicodedata.normalize("NFC", text)
    return is_palindrome_relaxed(normalised)


def main() -> None:
    print(is_palindrome("racecar"), is_palindrome("hello"))
    print(is_palindrome_two_pointer("abba"), is_palindrome_two_pointer("abc"))
    print(is_palindrome_relaxed("A man, a plan, a canal: Panama"))
    print(is_palindrome_unicode("Été"))
    print(is_palindrome(""), is_palindrome("x"))


if __name__ == "__main__":
    main()
