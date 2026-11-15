# sort_kit

One `sort()` function over insertion, merge, quick, heap, counting and Python's built-in sort.

```bash
python3 -m sorts.sort_kit        # demo, self-check, small benchmark (from the repo root)
```

```python
from sorts.sort_kit import sort

sort([3, 1, 2], algo="merge")                       # [1, 2, 3]
sort(["bb", "a", "ccc"], key=len, reverse=True)     # ['ccc', 'bb', 'a']
```

- `algorithms.py` holds the implementations, all with the same `f(items, key)` signature.
- `__init__.py` is the public API (`sort`, `is_sorted`, `ALGORITHMS`).
- `reverse=True` keeps equal items in their original order, like `sorted(..., reverse=True)`.
- The standalone versions of these algorithms live next to this folder, e.g. `../merge_sort.py`.
