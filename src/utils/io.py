import math
from decimal import Decimal
import csv
from pathlib import Path
from typing import List

def load_instance(path: Path) -> tuple[list[tuple[int, int]], int]:
    """
    Lê instâncias do professor no formato Unicauca/Kaggle.
    """
    stem = path.name.replace('_items.csv', '').replace('_info.csv', '')
    folder = path.parent
    info = folder / f"{stem}_info.csv"
    items = folder / f"{stem}_items.csv"

    with info.open() as fh:
        header, cap = next(csv.reader(fh))
        W = int(cap)

    it: list[tuple[int, int]] = []
    with items.open() as fh:
        next(fh)
        for _, val, wt, *_ in csv.reader(fh):
            it.append((int(wt), int(val)))

    return it, W


def discover_instances(DATA_DIRS) -> List[Path]:
    """Return a sorted list with every instance file found under DATA_DIRS."""
    instances: List[Path] = []
    for root in DATA_DIRS:
        if root.exists():
            instances.extend(p for p in root.rglob("*.*") if p.is_file())
    return sorted(instances)


def load_completed(csv_path: Path) -> set[str]:
    """Return the set of instance basenames already present in *csv_path*."""
    if not csv_path.exists():
        return set()
    with csv_path.open(newline="", encoding="utf-8") as fh:
        return {row["instance"] for row in csv.DictReader(fh)}


def convert(txt: Path) -> None:
    stem, folder = txt.stem, txt.parent
    with txt.open() as fh:
        n, cap = map(Decimal, fh.readline().split())
        raw = [tuple(map(Decimal, ln.split())) for ln in fh if ln.strip()]

    def places(x: Decimal) -> int:
        t = x.as_tuple()
        return -t.exponent if t.exponent < 0 else 0

    d = max(max(places(v), places(w)) for v, w in raw)
    m = 10 ** d

    cap_i = int(cap * m)
    items_i = [(int(w * m), int(v * m)) for v, w in raw]

    with (folder / f"{stem}_info.csv").open("w", newline="") as fh:
        csv.writer(fh).writerow(["c", cap_i])

    items_csv = folder / f"{stem}_items.csv"
    with items_csv.open("w", newline="") as fh:
        wcsv = csv.writer(fh)
        wcsv.writerow(["item", "value", "weight", "sol"])
        for i, (w_i, v_i) in enumerate(items_i, 1):
            wcsv.writerow([i, v_i, w_i, 0])

    print("✓", txt.name, f"(×{m} para inteiros)")
