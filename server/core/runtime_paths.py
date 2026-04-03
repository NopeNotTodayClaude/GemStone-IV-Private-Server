"""
Runtime path helpers.

Keeps the project portable by resolving everything from the repo root
instead of a fixed drive letter.
"""

from __future__ import annotations

import os
from pathlib import Path


def project_root() -> Path:
    override = str(os.environ.get("GEMSTONE_ROOT") or "").strip()
    if override:
        candidate = Path(override).expanduser().resolve()
        if candidate.exists():
            return candidate
    here = Path(__file__).resolve()
    for parent in [here] + list(here.parents):
        if (parent / "server").exists() and (parent / "scripts").exists() and (parent / "config").exists():
            return parent
    return here.parents[2]


def root_join(*parts: str) -> str:
    return str(project_root().joinpath(*parts))


def env_or_root(env_name: str, *parts: str) -> str:
    raw = str(os.environ.get(env_name) or "").strip()
    if raw:
        return str(Path(raw).expanduser())
    return root_join(*parts)


def first_existing(*paths: str) -> str:
    for path in paths:
        if path and Path(path).exists():
            return str(Path(path))
    return ""
