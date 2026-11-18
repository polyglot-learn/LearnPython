# dp_kit

Six classic dynamic-programming problems that return the actual solution, plus a `memoize` decorator.

```bash
python3 -m dynamic_programming.dp_kit     # seven examples plus a self-check
```

| Function | Returns |
|---|---|
| `knapsack(weights, values, capacity)` | best value and the chosen item indexes |
| `lcs(a, b)` | a longest common subsequence |
| `edit_distance(a, b)` | Levenshtein distance |
| `coin_change(coins, amount)` | the fewest coins, or `None` |
| `lis(nums)` | a longest strictly increasing subsequence |
| `count_paths(rows, cols, blocked)` | number of right/down paths |

Standalone versions live next to this folder, e.g. `../knapsack_01.py`.
