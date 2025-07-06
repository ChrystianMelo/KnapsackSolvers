from pathlib import Path
from utils import runner as runner
from utils import io as io

if __name__ == "__main__":

    DATA_DIR = Path("data/low_dimensional")
    for txt in DATA_DIR.rglob("*.txt"):
        io.convert(txt)
        print("✓", txt.relative_to(DATA_DIR))
        txt.unlink()

    runner.run(0.02, True)
