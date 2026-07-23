"""A stack-based virtual machine: compile expressions to bytecode, then run it.

Most language runtimes — CPython, the JVM, the .NET CLR — execute a compiled
bytecode on a virtual stack machine rather than walking the syntax tree every
time. This file builds the whole pipeline in miniature: a tokeniser, a
recursive-descent compiler that emits bytecode, and an interpreter loop that
executes it against an operand stack.

The stack machine has no registers. Each instruction pops its operands off the
stack and pushes its result, so `2 + 3 * 4` compiles to: push 2, push 3, push 4,
multiply, add. Operator precedence is resolved once at compile time, so the
runtime loop is a flat, fast dispatch with no parsing.

Compiling is O(n) in the source; execution is O(number of instructions).
"""

from dataclasses import dataclass

# Opcodes.
PUSH, ADD, SUB, MUL, DIV, NEG, LOAD, STORE = range(8)


@dataclass
class Instr:
    op: int
    arg: float | str | None = None


class Compiler:
    """Recursive descent that emits bytecode instead of building an AST."""

    def __init__(self, source: str) -> None:
        self.tokens = self._tokenize(source)
        self.pos = 0
        self.code: list[Instr] = []

    @staticmethod
    def _tokenize(source: str) -> list[str]:
        tokens, i = [], 0
        while i < len(source):
            ch = source[i]
            if ch.isspace():
                i += 1
            elif ch in "+-*/()=":
                tokens.append(ch)
                i += 1
            elif ch.isdigit() or ch == ".":
                j = i
                while j < len(source) and (source[j].isdigit() or source[j] == "."):
                    j += 1
                tokens.append(source[i:j])
                i = j
            elif ch.isalpha():
                j = i
                while j < len(source) and source[j].isalnum():
                    j += 1
                tokens.append(source[i:j])
                i = j
            else:
                raise SyntaxError(f"bad character {ch!r}")
        return tokens

    def _peek(self) -> str | None:
        return self.tokens[self.pos] if self.pos < len(self.tokens) else None

    def _next(self) -> str:
        tok = self.tokens[self.pos]
        self.pos += 1
        return tok

    def compile(self) -> list[Instr]:
        # Optional assignment: "name = expr".
        if len(self.tokens) >= 2 and self.tokens[1] == "=":
            name = self._next()
            self._next()  # '='
            self._expr()
            self.code.append(Instr(STORE, name))
        else:
            self._expr()
        return self.code

    def _expr(self) -> None:  # + and -
        self._term()
        while self._peek() in ("+", "-"):
            op = self._next()
            self._term()
            self.code.append(Instr(ADD if op == "+" else SUB))

    def _term(self) -> None:  # * and /
        self._factor()
        while self._peek() in ("*", "/"):
            op = self._next()
            self._factor()
            self.code.append(Instr(MUL if op == "*" else DIV))

    def _factor(self) -> None:
        tok = self._peek()
        if tok == "-":  # unary minus
            self._next()
            self._factor()
            self.code.append(Instr(NEG))
        elif tok == "(":
            self._next()
            self._expr()
            self._next()  # ')'
        elif tok and (tok[0].isdigit() or tok[0] == "."):
            self.code.append(Instr(PUSH, float(self._next())))
        else:  # a variable reference
            self.code.append(Instr(LOAD, self._next()))


def run(code: list[Instr], variables: dict[str, float]) -> float | None:
    stack: list[float] = []
    for instr in code:
        if instr.op == PUSH:
            stack.append(instr.arg)
        elif instr.op == LOAD:
            stack.append(variables[instr.arg])
        elif instr.op == STORE:
            variables[instr.arg] = stack[-1]
        elif instr.op == NEG:
            stack.append(-stack.pop())
        else:
            b, a = stack.pop(), stack.pop()
            stack.append({ADD: a + b, SUB: a - b, MUL: a * b, DIV: a / b}[instr.op])
    return stack[-1] if stack else None


OPNAME = {PUSH: "PUSH", ADD: "ADD", SUB: "SUB", MUL: "MUL", DIV: "DIV",
          NEG: "NEG", LOAD: "LOAD", STORE: "STORE"}


def main() -> None:
    variables: dict[str, float] = {}

    print("compile '2 + 3 * 4' to bytecode:")
    code = Compiler("2 + 3 * 4").compile()
    for instr in code:
        print(f"  {OPNAME[instr.op]}{'' if instr.arg is None else ' ' + str(instr.arg)}")
    print(f"  result = {run(code, variables)}  (precedence resolved at compile time)")

    programs = [
        "1 + 2 + 3 + 4",
        "(1 + 2) * (3 + 4)",
        "-5 + 3",
        "2 * -(3 + 1)",
        "10 / 4",
    ]
    for source in programs:
        result = run(Compiler(source).compile(), variables)
        print(f"  {source:<22} = {result}  (Python says {eval(source)})")

    print("variables persist across programs:")
    for source in ("x = 5 + 5", "y = x * 2", "x + y"):
        result = run(Compiler(source).compile(), variables)
        print(f"  {source:<12} -> {result}, vars = {variables}")


if __name__ == "__main__":
    main()
