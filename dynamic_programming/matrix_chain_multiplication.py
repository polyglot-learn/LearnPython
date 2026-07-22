"""Matrix chain multiplication: parenthesise a product of matrices so the total
scalar multiplication count is smallest.

Matrix product is associative, so the result never changes, but the cost does.
Multiplying a p by q matrix with a q by r matrix costs p * q * r, and for a
chain of dimensions 10x30, 30x5, 5x60 the two bracketings cost 1500+3000 and
9000+18000 — a factor of six apart.

The chain is described by a dimensions list of length n+1, where matrix i is
dims[i] by dims[i+1]. The state is cost[i][j], the cheapest way to multiply
matrices i through j. Any bracketing has a final multiplication, splitting the
range at some k, so cost[i][j] is the minimum over k of
cost[i][k] + cost[k+1][j] + dims[i] * dims[k+1] * dims[j+1]. This is interval
dynamic programming: solve short ranges first so longer ones can read them.

Storing the winning k for each range prints the parenthesisation.

Complexity: O(n**3) time and O(n**2) space.
"""

INF = float("inf")


def matrix_chain_order(dims: list[int]) -> tuple[int, list[list[int]]]:
    """Return the minimum scalar multiplications and the split table."""
    n = len(dims) - 1  # number of matrices
    if n <= 0:
        return 0, []
    cost = [[0] * n for _ in range(n)]
    split = [[0] * n for _ in range(n)]
    for length in range(2, n + 1):          # ranges grow shortest first
        for i in range(n - length + 1):
            j = i + length - 1
            cost[i][j] = INF
            for k in range(i, j):
                trial = (cost[i][k] + cost[k + 1][j]
                         + dims[i] * dims[k + 1] * dims[j + 1])
                if trial < cost[i][j]:
                    cost[i][j] = trial
                    split[i][j] = k
    return int(cost[0][n - 1]), split


def parenthesise(split: list[list[int]], i: int, j: int,
                 names: list[str]) -> str:
    if i == j:
        return names[i]
    k = split[i][j]
    return f"({parenthesise(split, i, k, names)}"\
           f" x {parenthesise(split, k + 1, j, names)})"


def naive_left_to_right_cost(dims: list[int]) -> int:
    """Cost of the obvious ((A B) C) D order, for comparison."""
    total = 0
    rows = dims[0]
    for i in range(1, len(dims) - 1):
        total += rows * dims[i] * dims[i + 1]
    return total


def describe(dims: list[int]) -> None:
    n = len(dims) - 1
    names = [chr(ord("A") + i) for i in range(n)]
    shapes = ", ".join(f"{names[i]}={dims[i]}x{dims[i + 1]}" for i in range(n))
    best, split = matrix_chain_order(dims)
    print(f"dims {dims}")
    print(f"  matrices: {shapes}")
    print(f"  optimal cost {best} via {parenthesise(split, 0, n - 1, names)}")
    print(f"  left-to-right cost {naive_left_to_right_cost(dims)}")


def main() -> None:
    describe([10, 30, 5, 60])
    describe([40, 20, 30, 10, 30])
    describe([5, 10, 3, 12, 5, 50, 6])

    print("\nedge cases:")
    print("  single matrix, dims [4, 7]:", matrix_chain_order([4, 7])[0])
    print("  no matrices, dims [4]:     ", matrix_chain_order([4])[0])

    best, split = matrix_chain_order([2, 3, 4])
    print("  two matrices 2x3 and 3x4:  ", best,
          parenthesise(split, 0, 1, ["A", "B"]))
    assert best == 2 * 3 * 4


if __name__ == "__main__":
    main()
