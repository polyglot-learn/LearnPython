"""Reading and writing files with `pathlib`.

`Path` replaces string concatenation and most of `os.path`: the `/` operator
joins segments correctly on every platform, and the object carries methods for
everything you used to import separately.

Two habits worth forming:
  - Always open text files with an explicit `encoding="utf-8"`. The default is
    platform-dependent, which is how "works on my machine" bugs are born.
  - Iterate a file object rather than calling `.read()`; it streams line by
    line and works on a file larger than memory.

This sample writes only inside a temporary directory that it removes.
"""

import tempfile
from pathlib import Path


def main() -> None:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        data = root / "notes" / "todo.txt"  # `/` joins path segments
        data.parent.mkdir(parents=True, exist_ok=True)

        # Whole-file convenience methods.
        data.write_text("alpha\nbeta\ngamma\n", encoding="utf-8")
        print(f"read_text -> {data.read_text(encoding='utf-8')!r}")

        # Streaming: one line at a time, constant memory.
        with data.open(encoding="utf-8") as fh:
            for lineno, line in enumerate(fh, start=1):
                print(f"  {lineno}: {line.rstrip()}")

        # Appending.
        with data.open("a", encoding="utf-8") as fh:
            fh.write("delta\n")
        print(f"lines now: {data.read_text(encoding='utf-8').splitlines()}")

        # Path attributes, no string surgery required.
        print(f"name={data.name} stem={data.stem} suffix={data.suffix}")
        print(f"parent={data.parent.name} exists={data.exists()} size={data.stat().st_size}B")

        # Globbing.
        (root / "notes" / "done.txt").write_text("x", encoding="utf-8")
        print(f"glob *.txt -> {sorted(p.name for p in root.rglob('*.txt'))}")

        # Binary mode deals in bytes, with no encoding involved.
        blob = root / "data.bin"
        blob.write_bytes(b"\x00\x01\x02")
        print(f"bytes -> {blob.read_bytes()!r}")

        # Missing files raise; that is usually what you want.
        try:
            (root / "nope.txt").read_text(encoding="utf-8")
        except FileNotFoundError as exc:
            print(f"FileNotFoundError: {exc.strerror}")

    print(f"temporary directory removed: {not Path(tmp).exists()}")


if __name__ == "__main__":
    main()
