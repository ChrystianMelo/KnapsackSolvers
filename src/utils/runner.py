import csv
import functools
from pathlib import Path
import sys
import time
import tracemalloc
from typing import Callable, List, Tuple, Union
from utils.io import convert, discover_instances, load_completed, load_instance
from utils.timeout import Timeout
import utils.solvers

TIME_LIMIT = 600  # 1_800 # 30min
SolverFn = Callable[..., Tuple[int, bool]]


def bnb(path: Path):
    '''Resolve a mochila usando Branch-and-Bound exato.'''
    items, W = load_instance(path)
    value, _ = utils.solvers.knapsack_bnb(items, W)
    return value, True


def aproximativo(path: Path, eps: float):
    '''Resolve a mochila com FPTAS (erro ε).'''
    items, W = load_instance(path)
    value, _ = utils.solvers.knapsack_fptas(items, W, eps)
    return value, True


def approx2(path: Path):
    """Resolve a mochila com o algoritmo 2-aproximativo."""
    items, W = load_instance(path)
    value, _ = utils.solvers.knapsack_two_approx(items, W)
    return value, True


def _peak_rss_mb() -> float:
    '''Retorna o pico de memória (RSS) em MB medido via tracemalloc.'''
    _, peak = tracemalloc.get_traced_memory()
    return peak / (1024 ** 2)


def run_solver(
    solver: SolverFn,
    instance: Path,
    *,
    eps: float,
) -> Tuple[str, Union[float, str], Union[float, str], Union[int, str], str]:
    '''Executa o solver com timeout, mede tempo/memória e devolve linha de resultado.'''
    start = time.perf_counter()
    tracemalloc.start()
    status = "ok"
    try:
        with Timeout(TIME_LIMIT):
            if solver is aproximativo:

                value, feasible = solver(instance, eps)
            else:
                value, feasible = solver(instance)
    except (TimeoutError, KeyboardInterrupt):
        status = "timeout"
        value, feasible = "NA", False
    except Exception as exc:
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


def run(epsilon=float, force=bool, DATA_DIRS=List[Path], RESULTS_DIR=Path) -> None:
    '''Dispara todos os solvers sobre todas as instâncias e grava CSVs de saída.'''

    tasks: List[Tuple[str, SolverFn, Path]] = [
        ("bnb",         bnb,          RESULTS_DIR / "bnb_results.csv"),
        ("2approx",     approx2,      RESULTS_DIR / "2approx_results.csv"),
        (f"fptas_eps{epsilon}", functools.partial(aproximativo, eps=epsilon),
         RESULTS_DIR / "fptas_results.csv"),
    ]

    instances = [p for p in discover_instances(
        DATA_DIRS) if p.name.endswith('.csv')]

    if not instances:
        sys.stderr.write(
            "No instance files found under ./data/. Did you download the datasets?\n")
        sys.exit(2)

    for label, solver, csv_path in tasks:
        seen = load_completed(csv_path) if not force else set()
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
                row = run_solver(solver, inst, eps=epsilon)
                writer.writerow(row)
                fh.flush()

    print("\n[✓] Benchmark finished. Results stored under ./results/.")
