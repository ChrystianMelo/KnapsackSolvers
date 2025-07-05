import csv
import functools
import os
from pathlib import Path
import argparse
import sys
import time
import tracemalloc
from typing import Callable, List, Tuple, Union
from utils.io import discover_instances, load_completed, load_instance
from utils.timeout import Timeout
import utils.solvers


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
TIME_LIMIT = 1_800  # 30 min in seconds
SolverFn = Callable[..., Tuple[int, bool]]

def bnb(path: Path):
    items, W = load_instance(path)
    value, _sel = utils.solvers.knapsack_bnb(items, W)
    return value, True

def aproximativo(path: Path, eps: float):
    items, W = load_instance(path)
    value, _sel = utils.solvers.knapsack_fptas(items, W, eps)
    return value, True

def _peak_rss_mb() -> float:
    """Best‑effort peak RSS in MiB using ``resource``; falls back to tracemalloc."""
    _, peak = tracemalloc.get_traced_memory()
    return peak / (1024 ** 2)


def run_solver(
    solver: SolverFn,
    instance: Path,
    *,
    eps: float,
) -> Tuple[str, Union[float, str], Union[float, str], Union[int, str], str]:
    """Execute ``solver`` on *instance*, enforcing TIME_LIMIT and collecting metrics."""
    start = time.perf_counter()
    tracemalloc.start()
    status = "ok"
    try:
        with Timeout(TIME_LIMIT):
            if solver is aproximativo:
                # type: ignore[arg-type]
                value, feasible = solver(instance, eps)
            else:
                value, feasible = solver(instance)  # type: ignore[arg-type]
    except TimeoutError:
        status = "timeout"
        value, feasible = "NA", False
    except Exception as exc:  # pragma: no cover – unexpected failure
        status = f"error:{exc.__class__.__name__}"
        value, feasible = "NA", False
    finally:
        runtime = time.perf_counter() - start
        mem_mb = _peak_rss_mb()
        tracemalloc.stop()

    if status != "ok":
        runtime = mem_mb = "NA"
    return (
        instance.name,
        runtime,
        mem_mb,
        value,
        status if status != "ok" else ("1" if feasible else "0"),
    )


def run(argv: List[str] | None = None) -> None:  # noqa: D401 – imperative mood
    parser = argparse.ArgumentParser(description="Benchmark knapsack solvers")
    parser.add_argument("--epsilon", "-e", type=float, default=0.10,
                        help="ε for the FPTAS 'aproximativo' (default: 0.10)")
    parser.add_argument("--force", "-f", action="store_true",
                        help="re‑run instances already present in CSVs")
    args = parser.parse_args(argv)

    RESULTS_DIR = Path("results")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    tasks: List[Tuple[str, SolverFn, Path]] = [
        ("bnb", bnb, RESULTS_DIR / "bnb_results.csv"),
        (f"aprox_eps{args.epsilon}", functools.partial(aproximativo, eps=args.epsilon),
         RESULTS_DIR / "aprox_results.csv"),
    ]

    instances = [p for p in discover_instances([
        Path("data/low_dimensional"),
        Path("data/large_scale"),
    ]) if p.name.endswith('.csv')]

    if not instances:
        sys.stderr.write(
            "No instance files found under ./data/. Did you download the datasets?\n")
        sys.exit(2)

    for label, solver, csv_path in tasks:
        seen = load_completed(csv_path) if not args.force else set()
        write_header = not csv_path.exists()
        with csv_path.open("a", newline="", encoding="utf-8") as fh:
            writer = csv.writer(fh)
            if write_header:
                writer.writerow(["instance", "time", "memory",
                                "profit", "status_or_feasible"])

            for inst in instances:
                if inst.name in seen:
                    continue
                print(
                    f"[INFO] {label:<12} ← {inst.relpath('.') if hasattr(inst, 'relpath') else inst}")
                row = run_solver(solver, inst, eps=args.epsilon)
                writer.writerow(row)
                fh.flush()

    print("\n[✓] Benchmark finished. Results stored under ./results/.")


if __name__ == "__main__":  # pragma: no cover
    run(["--epsilon", "0.02", "--force"])

