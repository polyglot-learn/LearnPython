"""Two classic pattern matchers by dynamic programming: glob wildcards and regex.

Both share one state: dp[i][j] is True when the first i characters of the text
are matched by the first j tokens of the pattern. The difference is entirely in
what '*' means.

In glob, '?' matches any single character and '*' matches any run (including
empty). So '*' has two transitions from dp[i][j]: use it as empty (dp[i][j-1])
or let it swallow one more text character (dp[i-1][j]) — that pair is why one
'*' can span a whole substring.

In regex here, '.' matches any single character and '*' modifies the *previous*
token, meaning "zero or more of it". So '*' again branches two ways: skip the
token pair entirely (dp[i][j-2]), or, if the previous token matches text[i-1],
consume that character and stay on the same '*' (dp[i-1][j]).
"""


def wildcard_match(text: str, pattern: str) -> bool:
    """Glob matching where '?' is any char and '*' is any run of chars."""
    n, m = len(text), len(pattern)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(1, m + 1):
        if pattern[j - 1] == "*":  # '*' can match the empty prefix of text
            dp[0][j] = dp[0][j - 1]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            p = pattern[j - 1]
            if p == "*":
                dp[i][j] = dp[i][j - 1] or dp[i - 1][j]  # empty, or eat one char
            elif p == "?" or p == text[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    return dp[n][m]


def regex_match(text: str, pattern: str) -> bool:
    """Regex matching where '.' is any char and 'x*' is zero or more of x."""
    n, m = len(text), len(pattern)
    dp = [[False] * (m + 1) for _ in range(n + 1)]
    dp[0][0] = True
    for j in range(2, m + 1):
        if pattern[j - 1] == "*":  # 'x*' can match empty, dropping the pair
            dp[0][j] = dp[0][j - 2]
    for i in range(1, n + 1):
        for j in range(1, m + 1):
            p = pattern[j - 1]
            if p == "*":
                prev = pattern[j - 2]
                zero = dp[i][j - 2]  # take zero copies of the token
                more = dp[i - 1][j] and (prev == "." or prev == text[i - 1])
                dp[i][j] = zero or more
            elif p == "." or p == text[i - 1]:
                dp[i][j] = dp[i - 1][j - 1]
    return dp[n][m]


def main() -> None:
    glob_cases = [
        ("aa", "a", False), ("aa", "*", True), ("cb", "?a", False),
        ("adceb", "*a*b", True), ("acdcb", "a*c?b", False),
        ("", "*", True), ("", "", True), ("abc", "a*c", True),
    ]
    print("glob wildcard:")
    for text, pat, want in glob_cases:
        got = wildcard_match(text, pat)
        assert got == want, (text, pat, got, want)
        print(f"  match({text!r:9}, {pat!r:8}) = {got}")

    regex_cases = [
        ("aa", "a", False), ("aa", "a*", True), ("ab", ".*", True),
        ("aab", "c*a*b", True), ("mississippi", "mis*is*p*.", False),
        ("", "", True), ("", "a*", True), ("abc", "a.c", True),
        ("aaa", "a*a", True),
    ]
    print("regex . and *:")
    for text, pat, want in regex_cases:
        got = regex_match(text, pat)
        assert got == want, (text, pat, got, want)
        print(f"  match({text!r:13}, {pat!r:12}) = {got}")

    # Cross-check regex against Python's own re on fully-anchored patterns.
    import re
    for text, pat, _ in regex_cases:
        assert regex_match(text, pat) == bool(re.fullmatch(pat, text)), (text, pat)
    print("regex matcher agrees with re.fullmatch on all cases")


if __name__ == "__main__":
    main()
