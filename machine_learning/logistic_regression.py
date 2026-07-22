"""Logistic regression: a linear boundary squashed into a probability.

The model computes a linear score z = b + w.x and pushes it through the sigmoid
1 / (1 + e^-z), which maps any real number into (0, 1) and can be read as
P(y = 1 | x). Fitting means choosing b and w to maximise the likelihood of the
labels, which is the same as minimising the log-loss
-mean(y log p + (1 - y) log(1 - p)).

The pleasant surprise is the gradient. Despite the sigmoid, the derivative of the
log-loss with respect to each weight is just mean((p - y) * x) — identical in shape
to linear regression's gradient. The loss is convex, so plain gradient descent
reaches the global optimum.

Predicting a class means thresholding at p = 0.5, which is exactly the line
b + w.x = 0. That line is printed below, so you can see the geometry the numbers
encode. Training costs O(iters * n * d); prediction is O(d).
"""

import math
import random


def sigmoid(z: float) -> float:
    """Numerically stable: exp of a large positive number would overflow."""
    if z >= 0:
        return 1 / (1 + math.exp(-z))
    e = math.exp(z)
    return e / (1 + e)


def log_loss(ys: list[int], probs: list[float]) -> float:
    eps = 1e-12  # keeps log(0) from blowing up on a confident correct guess
    total = 0.0
    for y, p in zip(ys, probs):
        p = min(max(p, eps), 1 - eps)
        total += -(y * math.log(p) + (1 - y) * math.log(1 - p))
    return total / len(ys)


def probabilities(rows: list[list[float]], weights: list[float],
                  bias: float) -> list[float]:
    return [sigmoid(bias + sum(w * v for w, v in zip(weights, row))) for row in rows]


def fit(rows: list[list[float]], ys: list[int], lr: float = 0.1,
        iters: int = 4000) -> tuple[float, list[float], list[tuple[int, float]]]:
    """Return (bias, weights, [(iteration, loss)]) from batch gradient descent."""
    n, d = len(rows), len(rows[0])
    bias = 0.0
    weights = [0.0] * d
    history: list[tuple[int, float]] = []
    for step in range(iters + 1):
        probs = probabilities(rows, weights, bias)
        if step % (iters // 5) == 0:
            history.append((step, log_loss(ys, probs)))
        if step == iters:
            break
        errors = [p - y for p, y in zip(probs, ys)]
        bias -= lr * sum(errors) / n
        weights = [w - lr * sum(e * row[j] for e, row in zip(errors, rows)) / n
                   for j, w in enumerate(weights)]
    return bias, weights, history


def accuracy(ys: list[int], probs: list[float], threshold: float = 0.5) -> float:
    hits = sum(1 for y, p in zip(ys, probs) if (p >= threshold) == bool(y))
    return hits / len(ys)


def describe_boundary(bias: float, weights: list[float]) -> str:
    """For two features, b + w0*x + w1*y = 0 rearranges to y = m*x + c."""
    w0, w1 = weights
    if w1 == 0:
        return f"x = {-bias / w0:.3f} (vertical)"
    return f"y = {-w0 / w1:.3f} * x + {-bias / w1:.3f}"


def main() -> None:
    rng = random.Random(11)

    # Two Gaussian blobs, mostly separable but with a little overlap.
    rows: list[list[float]] = []
    ys: list[int] = []
    for _ in range(120):
        rows.append([rng.gauss(2.0, 1.0), rng.gauss(2.0, 1.0)])
        ys.append(0)
    for _ in range(120):
        rows.append([rng.gauss(5.0, 1.0), rng.gauss(5.5, 1.0)])
        ys.append(1)

    bias, weights, history = fit(rows, ys, lr=0.3, iters=4000)
    print("training log-loss")
    for step, loss in history:
        print(f"  iteration {step:>5}: {loss:.5f}")

    print(f"\nbias    {bias:.4f}")
    print("weights " + ", ".join(f"{w:.4f}" for w in weights))
    print(f"decision boundary: {describe_boundary(bias, weights)}")

    probs = probabilities(rows, weights, bias)
    print(f"accuracy: {accuracy(ys, probs) * 100:.2f}%")
    print(f"final log-loss: {log_loss(ys, probs):.5f}")

    print("\nsample predictions")
    for point in ([1.0, 1.0], [3.5, 3.7], [6.0, 6.0], [2.0, 6.0]):
        p = probabilities([point], weights, bias)[0]
        print(f"  {point} -> P(class 1) = {p:.4f} -> class {int(p >= 0.5)}")

    # Moving the threshold trades false positives against false negatives.
    print("\nthreshold sweep")
    for t in (0.2, 0.5, 0.8):
        print(f"  threshold {t}: accuracy {accuracy(ys, probs, t) * 100:.2f}%")

    print("\nedge cases")
    print(f"  sigmoid(0)      = {sigmoid(0.0)}")
    print(f"  sigmoid(-800)   = {sigmoid(-800.0)}  (no overflow)")
    print(f"  sigmoid(800)    = {sigmoid(800.0)}")
    print(f"  log-loss of a confident wrong guess: "
          f"{log_loss([1], [0.0]):.3f}")
    print(f"  log-loss of a coin flip:             "
          f"{log_loss([1, 0], [0.5, 0.5]):.5f}  (= ln 2)")

    # A perfectly separable set drives the weights towards infinity; the loss
    # keeps falling but never reaches zero, which is why regularisation exists.
    easy = [[0.0, 0.0], [0.0, 1.0], [5.0, 5.0], [5.0, 6.0]]
    easy_y = [0, 0, 1, 1]
    e_bias, e_weights, e_hist = fit(easy, easy_y, lr=0.5, iters=4000)
    print(f"  separable data, final loss {e_hist[-1][1]:.6f}, "
          f"weight norm {math.hypot(*e_weights):.3f}")


if __name__ == "__main__":
    main()
