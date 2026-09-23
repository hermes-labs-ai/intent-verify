"""On-demand native Hermes Agent tool for Intent Verify's advisory coverage map."""

from __future__ import annotations

import json
from pathlib import Path

from .report import run_check, to_coverage_map_json

SCHEMA = {
    "name": "intent_verify_map",
    "description": (
        "Map acceptance items in an explicitly named Markdown spec to lexical evidence in "
        "explicitly named source or test paths. Use on demand for spec drift or handoff review. "
        "The result is advisory and never authorizes acceptance, merge, or release."
    ),
    "parameters": {
        "type": "object",
        "properties": {
            "spec_path": {"type": "string", "description": "Path to the Markdown spec file"},
            "repo_path": {"type": "string", "description": "Path to the repository to inspect"},
            "evidence_paths": {
                "type": "array",
                "items": {"type": "string"},
                "minItems": 1,
                "description": "Explicit repo-relative source or test files/directories to inspect",
            },
        },
        "required": ["spec_path", "repo_path", "evidence_paths"],
    },
}


def intent_verify_map(args: dict, **kwargs) -> str:
    """Use the canonical map engine with the CLI's explicit-path boundary."""
    spec = args.get("spec_path")
    repo = args.get("repo_path")
    roots = args.get("evidence_paths")
    if not isinstance(spec, str) or not spec.strip():
        return json.dumps({"error": "spec_path is required", "acceptance_authority": False})
    if not isinstance(repo, str) or not repo.strip():
        return json.dumps({"error": "repo_path is required", "acceptance_authority": False})
    if not isinstance(roots, list) or not roots or any(
        not isinstance(root, str) or not root.strip() for root in roots
    ):
        return json.dumps({
            "error": "evidence_paths must be a nonempty list of paths",
            "acceptance_authority": False,
        })

    try:
        repo_path = Path(repo).resolve()
        spec_path = Path(spec)
        if not repo_path.is_dir() or not spec_path.is_file():
            raise ValueError("repo_path must be a directory and spec_path must be a file")
        evidence_paths = [((repo_path / root).resolve()) for root in roots]
        if any(not path.is_relative_to(repo_path) or not path.exists()
               for path in evidence_paths):
            raise ValueError("every evidence path must exist within repo_path")
        return to_coverage_map_json(run_check(
            spec_path, repo_path, evidence_paths=evidence_paths
        ))
    except (OSError, UnicodeError, ValueError) as exc:
        return json.dumps({"error": str(exc), "acceptance_authority": False})


def register(ctx) -> None:
    ctx.register_tool(name="intent_verify_map", toolset="intent_verify",
                      schema=SCHEMA, handler=intent_verify_map)
