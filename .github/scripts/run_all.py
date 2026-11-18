"""Run every sample and report failures.

Single files run as scripts; a package directory (one containing __main__.py)
runs as ``python -m <dotted.path>`` from the repo root.
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TIMEOUT = 60


def targets() -> list[tuple[str, list[str]]]:
    found: list[tuple[str, list[str]]] = []
    for path in sorted(ROOT.rglob("*.py")):
        rel = path.relative_to(ROOT)
        if rel.parts[0] in {".git", ".github", ".venv", "venv"}:
            continue
        if path.name == "__main__.py":
            module = ".".join(rel.parent.parts)
            found.append((str(rel.parent), [sys.executable, "-m", module]))
        elif any((ROOT / Path(*rel.parts[:i]) / "__main__.py").exists()
                 for i in range(1, len(rel.parts))):
            continue  # internal module of a package; covered by its __main__
        else:
            found.append((str(rel), [sys.executable, str(rel)]))
    return found


def main() -> int:
    failures = 0
    items = targets()
    for name, cmd in items:
        try:
            result = subprocess.run(
                cmd, cwd=ROOT, capture_output=True, text=True,
                timeout=TIMEOUT, stdin=subprocess.DEVNULL,
            )
            ok = result.returncode == 0 and result.stdout.strip() != ""
            detail = (result.stderr.strip().splitlines() or ["no output"])[-1]
        except subprocess.TimeoutExpired:
            ok, detail = False, f"timeout after {TIMEOUT}s"
        if not ok:
            failures += 1
            print(f"FAIL {name}: {detail}")
    print(f"{len(items) - failures}/{len(items)} passed")
    return 1 if failures else 0


if __name__ == "__main__":
    sys.exit(main())
