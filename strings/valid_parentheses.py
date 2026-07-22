"""Balanced brackets — the canonical use of a stack.

Push each opener; on a closer, the top of the stack must be its match. The
string is balanced only if every closer matched and the stack ends empty.
Both failure modes matter: ")(" fails on the pop, "(" fails on the final check.

O(n) time, O(n) space in the worst case ("((((((").
"""

PAIRS = {")": "(", "]": "[", "}": "{"}


def is_balanced(text: str) -> bool:
    stack: list[str] = []
    for ch in text:
        if ch in PAIRS.values():
            stack.append(ch)
        elif ch in PAIRS:
            if not stack or stack.pop() != PAIRS[ch]:
                return False
    return not stack


def longest_valid_parentheses(text: str) -> int:
    """Length of the longest balanced run — stack of indices, base marker -1."""
    stack = [-1]
    best = 0
    for i, ch in enumerate(text):
        if ch == "(":
            stack.append(i)
        else:
            stack.pop()
            if stack:
                best = max(best, i - stack[-1])
            else:
                stack.append(i)  # new base for the next candidate run
    return best


def min_insertions_to_balance(text: str) -> int:
    open_needed = closers = 0
    for ch in text:
        if ch == "(":
            open_needed += 1
        elif open_needed:
            open_needed -= 1
        else:
            closers += 1  # an unmatched ')'
    return open_needed + closers


def main() -> None:
    for s in ("()[]{}", "(]", "([{}])", ")(", "((", ""):
        print(f"{s!r:10} balanced: {is_balanced(s)}")
    print(f"longest valid in ')()())' = {longest_valid_parentheses(')()())')}")
    print(f"insertions for '(()))(' = {min_insertions_to_balance('(()))(')}")


if __name__ == "__main__":
    main()
