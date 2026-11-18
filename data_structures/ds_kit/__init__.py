"""ds_kit: Stack, Queue, LinkedList, MinHeap, Trie and LRUCache.

    >>> from data_structures.ds_kit import Stack, Trie
    >>> s = Stack([1, 2, 3]); s.pop()
    3
    >>> t = Trie(); t.insert("tea"); t.insert("ten"); t.with_prefix("te")
    ['tea', 'ten']
"""

from .indexed import LRUCache, MinHeap, Trie
from .linear import LinkedList, Queue, Stack

__all__ = ["Stack", "Queue", "LinkedList", "MinHeap", "Trie", "LRUCache"]
