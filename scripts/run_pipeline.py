from __future__ import annotations

from pathlib import Path

# Allow scripts to run directly from the repository root without requiring pip install -e . first.
import sys
PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_DIR = PROJECT_ROOT / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))
import subprocess
import sys


def run(cmd: list[str]) -> None:
    print("+", " ".join(cmd))
    subprocess.run(cmd, check=True)


def main() -> None:
    run([sys.executable, "scripts/00_download_nbs_tables.py", "--skip-if-exists"])
    run([sys.executable, "scripts/03_build_features.py", "--mode", "quickstart"])
    run([sys.executable, "scripts/04_train_models.py"])
    run([sys.executable, "scripts/05_evaluate_and_explain.py"])


if __name__ == "__main__":
    main()
