"""Shunting-yard: infix to postfix with one stack, then evaluate the postfix.

Dijkstra's algorithm reads the infix tokens once. Operands go straight to the
output. An operator waits on a stack until an operator of lower precedence
arrives, at which point everything of higher-or-equal precedence is popped out
first. Left-associative operators pop on equal precedence, right-associative
ones do not — that single comparison is the whole difference between 8-4-2
meaning 2 and 2**3**2 meaning 512.

Parentheses are handled by pushing the open bracket as a fence that nothing pops
past, and popping back to it on the close. Unary minus needs care because the
character is shared with subtraction: it is unary exactly when it appears where
an operand was expected, so tracking that expectation is enough to tell them
apart. Here it becomes a distinct 'u-' operator with very high precedence.

Both passes are O(n), and the postfix form needs no brackets to evaluate.
"""

PRECEDENCE = {"+": 1, "-": 1, "*": 2, "/": 2, "%": 2, "**": 3, "u-": 4}
RIGHT_ASSOC = {"**", "u-"}


def tokenize(expr: str) -> list[str]:
    tokens: list[str] = []
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch.isspace():
            i += 1
        elif ch.isdigit() or ch == ".":
            j = i
            while j < len(expr) and (expr[j].isdigit() or expr[j] == "."):
                j += 1
            tokens.append(expr[i:j])
            i = j
        elif expr[i:i + 2] == "**":
            tokens.append("**")
            i += 2
        elif ch in "+-*/%()":
            tokens.append(ch)
            i += 1
        else:
            raise ValueError(f"unexpected character {ch!r} at position {i}")
    return tokens


def to_rpn(expr: str) -> list[str]:
    output: list[str] = []
    stack: list[str] = []
    expect_operand = True  # true at the start and right after any operator or '('

    for token in tokenize(expr):
        if token[0].isdigit() or token[0] == ".":
            if not expect_operand:
                raise ValueError(f"two operands in a row near {token!r}")
            output.append(token)
            expect_operand = False
        elif token == "(":
            stack.append(token)
            expect_operand = True
        elif token == ")":
            while stack and stack[-1] != "(":
                output.append(stack.pop())
            if not stack:
                raise ValueError("unbalanced ')'")
            stack.pop()
            expect_operand = False
        else:
            op = "u-" if token == "-" and expect_operand else token
            if expect_operand and op != "u-":
                raise ValueError(f"operator {token!r} where an operand was expected")
            while stack and stack[-1] != "(":
                top = stack[-1]
                if PRECEDENCE[top] > PRECEDENCE[op] or (
                    PRECEDENCE[top] == PRECEDENCE[op] and op not in RIGHT_ASSOC
                ):
                    output.append(stack.pop())
                else:
                    break
            stack.append(op)
            expect_operand = True

    while stack:
        top = stack.pop()
        if top == "(":
            raise ValueError("unbalanced '('")
        output.append(top)
    return output


def eval_rpn(tokens: list[str]) -> float:
    stack: list[float] = []
    for token in tokens:
        if token == "u-":
            stack.append(-stack.pop())
        elif token in PRECEDENCE:
            if len(stack) < 2:
                raise ValueError(f"not enough operands for {token!r}")
            b, a = stack.pop(), stack.pop()
            match token:
                case "+":
                    stack.append(a + b)
                case "-":
                    stack.append(a - b)
                case "*":
                    stack.append(a * b)
                case "/":
                    stack.append(a / b)
                case "%":
                    stack.append(a % b)
                case "**":
                    stack.append(a ** b)
        else:
            stack.append(float(token))
    if len(stack) != 1:
        raise ValueError("leftover operands: malformed expression")
    return stack[0]


def main() -> None:
    for expr in [
        "3 + 4 * 2",
        "(3 + 4) * 2",
        "8 - 4 - 2",          # left-associative
        "2 ** 3 ** 2",        # right-associative
        "-5 + 3",             # unary minus at the start
        "4 * -(2 + 1)",       # unary minus after an operator
        "10 % 4 / 2",
    ]:
        rpn = to_rpn(expr)
        print(f"{expr:<14} -> {' '.join(rpn):<20} = {eval_rpn(rpn)}")

    print()
    for bad in ["(1 + 2", "1 + 2)", "3 * / 4", "1 2 +"]:
        try:
            eval_rpn(to_rpn(bad))
        except ValueError as exc:
            print(f"{bad!r} -> {exc}")

    print()
    print(f"empty expression tokenizes to {to_rpn('')}")


if __name__ == "__main__":
    main()
