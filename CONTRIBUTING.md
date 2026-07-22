# Contributing to LearnPython

Thanks for helping grow the collection. This repo follows a few simple conventions so learners can browse it easily and so the git history stays useful as a learning artifact of its own.

## File conventions

1. **One concept per file.** If a topic can be split into two independent pieces, make two files.
2. **Every file is runnable.** Include a `main()` function guarded by `if __name__ == "__main__":` that demonstrates the code. A reader should be able to `python3 <path>` any file in the repo and see output.
3. **`basics/` files include teaching comments.** Explain *what* the code does and *why*, in plain English, for a first-time learner. Algorithm files stay clean — comment only when the *why* is non-obvious.
4. **Modern Python (3.10+).** Use type hints, f-strings, `match` statements, `dataclass`, and built-in generics (`list[int]`, not `List[int]`) where they make the code clearer.
5. **No dependencies.** Every sample runs against the standard library alone. If a sample truly needs a package, open an issue first.

## Commit and PR conventions

- **One file per commit** whenever the file stands alone.
- **One commit per pull request.** Small PRs are easy to review; that is the point.
- **Branch name:** `feature/<short-slug>`, e.g. `feature/quick-sort`.
- **Break a sample into multiple commits** when it contains independently understandable pieces — e.g. an iterative version and a recursive version of the same algorithm.
- **Commit message format:** `Add: <path> — <one-line what it teaches>`
  - Example: `Add: sorts/bubble_sort.py — iterative bubble sort with in-place swap`

## Naming

- Directories: `snake_case`, numeric-prefixed only inside `basics/` (to enforce reading order).
- Files: `snake_case.py`, descriptive over clever. `binary_search_recursive.py` beats `bsr.py`.

## Before opening a PR

- Run the file: `python3 <path>` — it must print something and exit 0.
- Keep it PEP 8 clean (4-space indent, `snake_case`, ≤ 88 column soft limit).
- Update `DIRECTORY.md` if you added new files.
