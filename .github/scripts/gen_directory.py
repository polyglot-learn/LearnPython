"""Regenerate DIRECTORY.md; with --check, fail if it is out of date."""

import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
SKIP = {".git", ".github", ".venv", "venv", "__pycache__"}

HEADER = """# Directory

Every `.py` file in this repo, grouped by category. Any file can be run with `python3 <path>`.
Packages (folders with a `__main__.py`) are run with `python3 -m <dotted.path>`.
"""


def is_package(path: Path) -> bool:
    return path.is_dir() and (path / "__main__.py").exists()


def groups() -> dict[str, list[Path]]:
    found: dict[str, list[Path]] = {}
    for directory in sorted(p for p in ROOT.rglob("*") if p.is_dir()):
        rel = directory.relative_to(ROOT)
        if any(part in SKIP or part.startswith(".") for part in rel.parts):
            continue
        if any(is_package(ROOT / Path(*rel.parts[:i])) for i in range(1, len(rel.parts) + 1)):
            continue  # inside a package
        entries = [f for f in sorted(directory.glob("*.py"))]
        entries += [d for d in sorted(directory.iterdir()) if is_package(d)]
        if entries:
            found[rel.as_posix()] = sorted(entries, key=lambda p: p.name)
    return found


def render() -> str:
    data = groups()
    total = sum(len(v) for v in data.values())
    lines = [HEADER, f"_{total} runnable samples across {len(data)} directories._\n"]
    for name, entries in data.items():
        lines.append(f"## {name}")
        for entry in entries:
            rel = entry.relative_to(ROOT).as_posix()
            if entry.is_dir():
                lines.append(f"- [{entry.name}]({rel}/) (package)")
            else:
                lines.append(f"- [{entry.stem}]({rel})")
        lines.append("")
    return "\n".join(lines)


def main() -> int:
    text = render()
    target = ROOT / "DIRECTORY.md"
    if "--check" in sys.argv:
        if target.read_text() != text:
            print("DIRECTORY.md is out of date: run python3 .github/scripts/gen_directory.py")
            return 1
        print("DIRECTORY.md is up to date")
        return 0
    target.write_text(text)
    return 0


if __name__ == "__main__":
    sys.exit(main())
