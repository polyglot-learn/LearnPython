"""`csv` — reading and writing tabular text without reinventing the quoting.

CSV looks like "split on commas" until a field contains a comma, a quote, or a
newline. The module handles all three, plus dialects (Excel, tab-separated) and
the quoting rules that go with them.

Two habits: open files with `newline=""` so the module controls line endings,
and use `DictReader`/`DictWriter` so code refers to column names rather than
positions that shift the moment someone adds a column.

For a streaming pipeline, keep the reader lazy and use generators — the whole
file never has to be in memory.
"""

import csv
import io
from collections import defaultdict
from dataclasses import dataclass


RAW = '''name,city,amount,note
Ada,London,120.50,"first, and best"
Alan,Manchester,80.00,"said ""hello"""
Grace,New York,240.75,"multi
line note"
Katherine,Hampton,,missing amount
'''


@dataclass
class Row:
    name: str
    city: str
    amount: float | None
    note: str


def parse(text: str) -> list[Row]:
    reader = csv.DictReader(io.StringIO(text))
    return [
        Row(
            name=r["name"],
            city=r["city"],
            amount=float(r["amount"]) if r["amount"] else None,
            note=r["note"],
        )
        for r in reader
    ]


def main() -> None:
    rows = parse(RAW)
    print("parsed rows:")
    for row in rows:
        print(f"  {row.name:<10} {row.city:<12} {row.amount!s:<8} {row.note!r}")

    print("\nquoting and embedded newlines survived:")
    print(f"  Alan's note: {rows[1].note!r}")
    print(f"  Grace's note has a newline: {chr(10) in rows[2].note}")

    print("\ngroup and aggregate:")
    totals: defaultdict[str, float] = defaultdict(float)
    for row in rows:
        totals[row.city] += row.amount or 0.0
    for city, total in sorted(totals.items(), key=lambda kv: -kv[1]):
        print(f"  {city:<12} {total:8.2f}")

    print("\nwriting, with quoting handled for us:")
    out = io.StringIO()
    writer = csv.DictWriter(out, fieldnames=["name", "total"], quoting=csv.QUOTE_MINIMAL)
    writer.writeheader()
    for row in rows:
        writer.writerow({"name": row.name, "total": f"{row.amount or 0:.2f}"})
    print("  " + out.getvalue().replace("\n", "\n  ").rstrip())

    print("dialects:")
    tsv = io.StringIO()
    csv.writer(tsv, delimiter="\t").writerows([["a", "b"], ["1", "2"]])
    print(f"  tab-separated: {tsv.getvalue()!r}")
    print(f"  registered dialects: {csv.list_dialects()}")

    print("\nsniffing an unknown file:")
    sample = "a;b;c\n1;2;3\n"
    dialect = csv.Sniffer().sniff(sample)
    print(f"  detected delimiter: {dialect.delimiter!r}, "
          f"has header: {csv.Sniffer().has_header(sample)}")

    print("\nstreaming stays lazy — never load a big file whole:")
    reader = csv.reader(io.StringIO(RAW))
    next(reader)  # skip the header
    print(f"  first two names: {[next(reader)[0] for _ in range(2)]}")


if __name__ == "__main__":
    main()
