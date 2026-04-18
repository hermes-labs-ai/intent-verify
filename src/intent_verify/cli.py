from __future__ import annotations

import argparse
import sys
from pathlib import Path

from .models import Verdict
from .report import run_check, to_json, to_text


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="intent-verify")
    subparsers = parser.add_subparsers(dest="command", required=True)

    check = subparsers.add_parser("check", help="check a repo against a markdown spec")
    check.add_argument("--spec", required=True, help="path to markdown spec file")
    check.add_argument("--repo", required=True, help="path to repo or source tree")
    check.add_argument("--section", help="optional section heading to target")
    check.add_argument("--json", action="store_true", help="emit JSON instead of text")
    check.add_argument(
        "--min-verified",
        type=float,
        default=0.7,
        help="average/item threshold for verified",
    )
    check.add_argument("--min-item", type=float, default=0.3, help="minimum per-item threshold")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command != "check":
        parser.error("unsupported command")

    spec_path = Path(args.spec)
    repo_path = Path(args.repo)
    if not spec_path.exists():
        print(f"intent-verify: spec not found: {spec_path}", file=sys.stderr)
        return 2
    if not repo_path.exists() or not repo_path.is_dir():
        print(f"intent-verify: repo path is not a directory: {repo_path}", file=sys.stderr)
        return 2
    if not 0 < args.min_item <= args.min_verified <= 1:
        print(
            "intent-verify: thresholds must satisfy 0 < min-item <= min-verified <= 1",
            file=sys.stderr,
        )
        return 2

    result = run_check(
        spec_path,
        repo_path,
        section=args.section,
        min_verified=args.min_verified,
        min_item=args.min_item,
    )
    print(to_json(result) if args.json else to_text(result))
    return {
        Verdict.VERIFIED: 0,
        Verdict.PARTIAL: 1,
        Verdict.MISSING: 2,
    }[result.verdict]


if __name__ == "__main__":
    raise SystemExit(main())
