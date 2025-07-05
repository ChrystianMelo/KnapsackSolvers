import csv
from pathlib import Path
from typing import List, Tuple


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
