"""Read-only bundled assets live separately from writable per-user data."""

import sys
from pathlib import Path


def resource_path(relative: str) -> str:
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parents[2]))
    return str(base / relative)
