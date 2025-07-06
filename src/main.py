import os
from pathlib import Path
from utils import runner as runner
from utils import io as io
from utils import analysis as analysis

if __name__ == "__main__":
    # Arquivos de testes que serão usados
    large_scale_examples = Path("data/large_scale")
    low_dimensional_examples = Path("data/low_dimensional")

    # Padroniza os arquivos de teste, se necessário.
    for txt in low_dimensional_examples.rglob("*.txt"):
        io.convert(txt)
        txt.unlink()
        print("✓", txt.relative_to(low_dimensional_examples))

    # Executa o programa
    DATA_DIRS = [large_scale_examples, low_dimensional_examples]
    RESULTS_DIR = Path("results")
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    runner.run(0.02, True, DATA_DIRS, RESULTS_DIR)

    # Analisa os resultados
    outdir = Path("reports")
    outdir.mkdir(exist_ok=True)
    result_files = [
        os.path.join(RESULTS_DIR, f)
        for f in os.listdir(RESULTS_DIR)
        if f.endswith('.csv') and os.path.isfile(os.path.join(RESULTS_DIR, f))
    ]
    opt = Path("data/optimal_output.csv")

    df = analysis.load_results(result_files, 1_800)
    df = analysis.add_rel_error(df, opt)

    # Tabelas resumo
    summary = analysis.summarise(df)
    summary.to_csv(outdir / "summary.csv", index=False)
    df.to_csv(outdir / "by_instance.csv", index=False)

    # Plotagens
    analysis.plot_time_vs_size(df, outdir)
    analysis.plot_mem_distribution(df, outdir)
    analysis.plot_error(df, outdir)
