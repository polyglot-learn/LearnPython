# search_kit

One `find()` over linear, binary, jump, exponential and interpolation search.

```bash
python3 -m searches.search_kit     # six examples plus a randomized self-check
```

```python
from searches.search_kit import find, contains

find([1, 3, 5, 7], 5)                                 # 2
find(["fig", "kiwi", "apple"], 4, key=len)            # 1
```

All algorithms except `linear` need input sorted by `key`. Duplicates return the leftmost index.
Standalone versions live next to this folder, e.g. `../binary_search.py`.
