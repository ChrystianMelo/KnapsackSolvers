from __future__ import annotations
from matplotlib.lines import Line2D
from pathlib import Path
import re
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import cm
plt.rcParams.update({
    "figure.autolayout": True,
    "axes.spines.right": False,
    "axes.spines.top": False,
})

###############################################################################
# Helpers
###############################################################################


def clean_instance_name(name: str) -> str:
    """Remove sufixos como *_info.csv*, *_items.csv*, extensões .csv/.txt."""
    name = re.sub(r"(_info|_items)?\.csv$", "", name)
    name = re.sub(r"\.txt$", "", name)
    return name


def algorithm_name(path: str | Path) -> str:
    """Inferir nome do algoritmo a partir do nome do arquivo."""
    stem = Path(path).stem
    stem = re.sub(r"(\.results?|_out|_run)$", "", stem)
    return stem


def parse_instance_meta(inst: str) -> dict[str, int | None]:
    """Extrai (n_items, capacity) de nomes *l‑d*; devolve Nones se falhar."""
    m = re.search(r"_kp_(\d+)_([\d]+)", inst)
    if not m:
        return {"n_items": None, "capacity": None}
    return {"n_items": int(m.group(1)), "capacity": int(m.group(2))}


def load_results(files: list[Path], timeout: int) -> pd.DataFrame:
    """Carrega todos os CSVs de resultados adicionando coluna *algorithm*."""
    frames = []
    for f in files:
        df = pd.read_csv(f)
        # normalizar nomes de instância
        df["instance"] = df["instance"].apply(clean_instance_name)
        df["algorithm"] = algorithm_name(f)
        # normalizar timeouts
        df["time"] = pd.to_numeric(df["time"], errors="coerce")
        df.loc[df["time"] > timeout, "time"] = float("nan")
        frames.append(df)
    data = pd.concat(frames, ignore_index=True)

    # anexar metadados das instâncias
    meta = data["instance"].apply(parse_instance_meta).apply(pd.Series)
    data = pd.concat([data, meta], axis=1)
    return data


def load_optimum(path: Path) -> pd.DataFrame:
    """Carrega tabela de ótimos no formato File,Optimum → (instance,opt)."""
    opt = pd.read_csv(path)
    opt = opt.rename(columns={"File": "instance", "Optimum": "opt"})
    opt["instance"] = opt["instance"].apply(clean_instance_name)
    opt["algorithm"] = "optimal"
    opt["time"] = opt["memory"] = float("nan")
    opt["status_or_feasible"] = "feasible"
    return opt

###############################################################################
# Métricas
###############################################################################


def summarise(data: pd.DataFrame) -> pd.DataFrame:
    """Gera resumo estatístico por algoritmo."""

    def feasible_mask(x: pd.Series) -> pd.Series:
        # considera “feasible”, 1, True como sucesso
        return x.astype(str).str.lower().isin(["feasible", "1", "true"])

    summary = (
        data.groupby("algorithm")
        .agg(
            instances=("instance", "nunique"),
            runs=("instance", "size"),
            avg_time=("time", "mean"),
            med_time=("time", "median"),
            max_time=("time", "max"),
            timeout_rate=("time", lambda s: s.isna().mean()),
            avg_mem=("memory", "mean"),  # MiB
            avg_profit=("profit", "mean"),
            success_rate=("status_or_feasible",
                          lambda s: feasible_mask(s).mean()),
        )
        .reset_index()
    )
    return summary.round(4)


def add_rel_error(
    data: pd.DataFrame,
    reference_alg: str | None = None,
    opt_col: str = "opt",
) -> pd.DataFrame:
    """Adiciona coluna *rel_error* (1 – profit/opt)."""
    if opt_col in data.columns:
        ref = data.set_index("instance")[opt_col]
    elif reference_alg and reference_alg in data["algorithm"].unique():
        ref = (
            data[data["algorithm"] == reference_alg]
            .set_index("instance")["profit"]
        )
    else:
        ref = data.groupby("instance")["profit"].max()

    data = data.join(ref.rename("profit_ref"), on="instance")
    data["rel_error"] = 1 - data["profit"] / data["profit_ref"]
    return data

###############################################################################
# Paleta & legenda compartilhadas
###############################################################################


def _alg_palette(names: List[str]):
    cmap = cm.get_cmap("tab10")
    return {n: cmap(i % 10) for i, n in enumerate(sorted(names))}


def _legend(ax, palette):
    handles = [Line2D([0], [0], marker="s", markersize=10, linestyle="", color=c, label=n)
               for n, c in palette.items()]
    ax.legend(handles=handles, title="Algoritmo", frameon=False, loc="best")

###############################################################################
# Visualizações (novas)
###############################################################################


def plot_time_vs_size(df: pd.DataFrame, outdir: Path):
    palette = _alg_palette(df["algorithm"].unique())
    fig, ax = plt.subplots()
    for name, g in df.groupby("algorithm"):
        jitter = np.random.normal(0, 0.15, size=len(g))  # evita sobreposição
        ax.scatter(g["n_items"] + jitter, g["time"], color=palette[name], label=name, alpha=0.8)
    ax.set_xlabel("n itens")
    ax.set_ylabel("Tempo (s)")
    ax.set_yscale("log")
    ax.set_title("Tempo × Tamanho da instância (escala log)")
    _legend(ax, palette)
    fig.savefig(outdir / "time_vs_size.png", dpi=150)


def _violin_strip(ax, data: pd.DataFrame, value: str, palette):
    algs = sorted(data["algorithm"].unique())
    positions = np.arange(len(algs)) + 1
    # violinos
    parts = ax.violinplot([data[data["algorithm"] == a][value].dropna() for a in algs],
                          positions=positions, showmeans=False, showmedians=False,
                          widths=0.8)
    for i, pc in enumerate(parts["bodies"]):
        pc.set_facecolor(palette[algs[i]])
        pc.set_alpha(0.5)
    # strip / swarm (valores individuais)
    for i, a in enumerate(algs):
        y = data[data["algorithm"] == a][value].dropna()
        x = np.random.normal(positions[i], 0.05, size=len(y))
        ax.scatter(x, y, s=12, color=palette[a], alpha=0.9, linewidth=0)
    ax.set_xticks(positions)
    ax.set_xticklabels(algs, rotation=30, ha="right")


def plot_mem_distribution(df: pd.DataFrame, outdir: Path):
    palette = _alg_palette(df["algorithm"].unique())
    fig, ax = plt.subplots()
    _violin_strip(ax, df, "memory", palette)
    ax.set_ylabel("MiB")
    ax.set_title("Distribuição de uso de memória")
    _legend(ax, palette)
    fig.savefig(outdir / "memory_violin.png", dpi=150)


def plot_error(df: pd.DataFrame, outdir: Path):
    if "rel_error" not in df.columns:
        return
    palette = _alg_palette(df["algorithm"].unique())
    fig, ax = plt.subplots()
    _violin_strip(ax, df, "rel_error", palette)
    ax.set_ylabel("Erro relativo")
    ax.set_title("Erro relativo (1 – profit/opt)")
    _legend(ax, palette)
    fig.savefig(outdir / "error_violin.png", dpi=150)