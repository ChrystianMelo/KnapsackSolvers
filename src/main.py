from pathlib import Path
from utils import runner as runner
from utils import io as io

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
    runner.run(0.02, True, DATA_DIRS, RESULTS_DIR)

    # Analisa os resultados
    # ...
