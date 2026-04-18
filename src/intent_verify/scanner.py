from __future__ import annotations

import os
from pathlib import Path

DEFAULT_EXTENSIONS = {
    ".cfg",
    ".go",
    ".ini",
    ".js",
    ".json",
    ".jsx",
    ".md",
    ".py",
    ".rs",
    ".sh",
    ".toml",
    ".ts",
    ".tsx",
    ".yaml",
    ".yml",
}

DEFAULT_SKIP_DIRS = {
    ".git",
    ".mypy_cache",
    ".next",
    ".pytest_cache",
    ".ruff_cache",
    ".venv",
    "__pycache__",
    "build",
    "dist",
    "node_modules",
    "target",
    "venv",
}


def load_repo_blobs(
    repo_path: Path,
    extensions: set[str] | None = None,
    exclude_paths: set[Path] | None = None,
) -> list[tuple[str, str]]:
    exts = extensions or DEFAULT_EXTENSIONS
    excluded = {path.resolve() for path in (exclude_paths or set())}
    blobs: list[tuple[str, str]] = []
    for root, dirs, files in os.walk(repo_path):
        dirs[:] = [
            name
            for name in dirs
            if name not in DEFAULT_SKIP_DIRS and not name.startswith(".")
        ]
        for name in files:
            suffix = Path(name).suffix.lower()
            if suffix not in exts:
                continue
            path = Path(root) / name
            if path.resolve() in excluded:
                continue
            try:
                blobs.append((str(path), path.read_text(encoding="utf-8", errors="ignore").lower()))
            except OSError:
                continue
    return blobs


def coverage_for_tokens(tokens: list[str], blobs: list[tuple[str, str]]) -> float:
    if not tokens:
        return 0.0
    found: set[str] = set()
    for _, blob in blobs:
        for token in tokens:
            if token in found:
                continue
            if token in blob:
                found.add(token)
        if len(found) == len(tokens):
            break
    return len(found) / len(tokens)
