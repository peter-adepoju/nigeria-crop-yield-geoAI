from __future__ import annotations

from pathlib import Path
from typing import Any

import yaml


def project_root() -> Path:
    """Return repository root based on this file location."""
    return Path(__file__).resolve().parents[2]


def load_config(path: str | Path = "configs/config.yaml") -> dict[str, Any]:
    """Load YAML configuration relative to the repository root if needed."""
    path = Path(path)
    if not path.is_absolute():
        path = project_root() / path
    with path.open("r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def resolve_path(path: str | Path) -> Path:
    """Resolve a project-relative path."""
    p = Path(path)
    return p if p.is_absolute() else project_root() / p
