from __future__ import annotations

import argparse
import json
import os
import re
import sys
from collections.abc import Mapping
from importlib.metadata import PackageNotFoundError, version
from pathlib import Path
from typing import Any

MAX_LABEL_LENGTH = 180
_REPOSITORY_RE = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
_REVISION_RE = re.compile(r"^[A-Fa-f0-9]{7,64}$")
_RELATIVE_PATH_RE = re.compile(r"^(?!/)(?!.*(?:^|/)\.\.(?:/|$))[A-Za-z0-9_.@/+\- ]+$")
_MAP_VERDICTS = {"covered", "partial", "gap"}
_ITEM_VERDICTS = {"covered", "partial", "gap"}


class SummaryPayloadError(ValueError):
    """Raised when a coverage-map payload is not safe to render."""


def _package_version() -> str:
    try:
        return version("intent-verify")
    except PackageNotFoundError:
        return "development"


def _label(value: object, *, limit: int = MAX_LABEL_LENGTH) -> str:
    """Return one bounded Markdown-table cell with formatting characters escaped."""
    text = str(value).replace("\r", " ").replace("\n", " ").strip()
    text = re.sub(r"\s+", " ", text)
    if len(text) > limit:
        text = f"{text[: limit - 1].rstrip()}…"
    return (
        text.replace("\\", "\\\\")
        .replace("|", "\\|")
        .replace("*", "\\*")
        .replace("_", "\\_")
        .replace("`", "\\`")
        .replace("[", "\\[")
        .replace("]", "\\]")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
    )


def _as_mapping(value: object, field: str) -> Mapping[str, Any]:
    if not isinstance(value, dict):
        raise SummaryPayloadError(f"coverage-map {field} must be an object")
    return value


def _as_list(value: object, field: str) -> list[Any]:
    if not isinstance(value, list):
        raise SummaryPayloadError(f"coverage-map {field} must be an array")
    return value


def parse_coverage_map(raw: str) -> Mapping[str, Any]:
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as error:
        raise SummaryPayloadError("coverage-map is not valid JSON") from error

    payload = _as_mapping(payload, "payload")
    if payload.get("schema_version") != "intent-verify.coverage-map.v1":
        raise SummaryPayloadError("coverage-map schema_version is not supported")
    if payload.get("signal_kind") != "lexical_scope_coverage":
        raise SummaryPayloadError("coverage-map signal_kind is not lexical_scope_coverage")
    if payload.get("acceptance_authority") is not False:
        raise SummaryPayloadError("coverage-map acceptance_authority must be false")
    if payload.get("verdict") not in _MAP_VERDICTS:
        raise SummaryPayloadError("coverage-map verdict is invalid")
    if payload.get("decision") not in {"review", "inspect"}:
        raise SummaryPayloadError("coverage-map decision is invalid")
    if not isinstance(payload.get("files_scanned"), int) or payload["files_scanned"] < 0:
        raise SummaryPayloadError("coverage-map files_scanned must be a non-negative integer")
    if not isinstance(payload.get("average_coverage"), (int, float)):
        raise SummaryPayloadError("coverage-map average_coverage must be numeric")

    _as_list(payload.get("evidence_roots"), "evidence_roots")
    items = _as_list(payload.get("items"), "items")
    for item in items:
        item = _as_mapping(item, "item")
        if not isinstance(item.get("text"), str):
            raise SummaryPayloadError("coverage-map item text must be a string")
        if item.get("verdict") not in _ITEM_VERDICTS:
            raise SummaryPayloadError("coverage-map item verdict is invalid")
        if not isinstance(item.get("coverage"), (int, float)):
            raise SummaryPayloadError("coverage-map item coverage must be numeric")
        _as_list(item.get("evidence_paths"), "item evidence_paths")
    return payload


def _source_link(payload: Mapping[str, Any], env: Mapping[str, str]) -> str | None:
    repository = env.get("GITHUB_REPOSITORY", "")
    revision = env.get("GITHUB_SHA", "")
    spec_path = payload.get("spec_path", "")
    if not (
        _REPOSITORY_RE.fullmatch(repository)
        and _REVISION_RE.fullmatch(revision)
        and isinstance(spec_path, str)
        and _RELATIVE_PATH_RE.fullmatch(spec_path)
    ):
        return None
    return f"https://github.com/{repository}/blob/{revision}/{spec_path}"


def _run_link(env: Mapping[str, str]) -> str | None:
    server_url = env.get("GITHUB_SERVER_URL", "https://github.com").rstrip("/")
    repository = env.get("GITHUB_REPOSITORY", "")
    run_id = env.get("GITHUB_RUN_ID", "")
    if not _REPOSITORY_RE.fullmatch(repository) or not run_id.isdigit():
        return None
    return f"{server_url}/{repository}/actions/runs/{run_id}"


def render_coverage_map_summary(
    payload: Mapping[str, Any], env: Mapping[str, str] | None = None
) -> str:
    """Render a bounded, advisory-only Markdown summary from a validated coverage map."""
    env = os.environ if env is None else env
    item_counts = {verdict: 0 for verdict in _ITEM_VERDICTS}
    for item in payload["items"]:
        item_counts[item["verdict"]] += 1

    source = _label(payload.get("spec_path", "unknown"))
    source_link = _source_link(payload, env)
    if source_link:
        source = f"[{source}]({source_link})"
    run_link = _run_link(env)
    run_text = f" · [workflow run]({run_link})" if run_link else ""
    roots = ", ".join(_label(root, limit=80) for root in payload["evidence_roots"]) or "none"

    lines = [
        "## intent-verify advisory coverage map",
        "",
        f"**{_label(payload['verdict']).upper()} · {_label(payload['decision'])}**{run_text}",
        "",
        (
            "This is lexical scope coverage only. Acceptance authority remains `false`; "
            "review, tests, and human judgment decide correctness and merge readiness."
        ),
        "",
        f"Package: `intent-verify {_package_version()}` · Spec: {source}",
        (
            f"Evidence roots: {roots} · Files scanned: {payload['files_scanned']} · "
            f"Average coverage: {float(payload['average_coverage']):.0%}"
        ),
        (
            f"Items: {item_counts['covered']} covered, "
            f"{item_counts['partial']} partial, {item_counts['gap']} gap."
        ),
        "",
        "| Status | Acceptance item | Coverage | Evidence files |",
        "| --- | --- | ---: | ---: |",
    ]
    for item in payload["items"]:
        lines.append(
            "| "
            f"{_label(item['verdict']).upper()} | {_label(item['text'])} | "
            f"{float(item['coverage']):.0%} | {len(item['evidence_paths'])} |"
        )
    return "\n".join(lines) + "\n"


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="intent-verify-summary",
        description="Render an opt-in GitHub Actions summary from a coverage-map JSON payload.",
    )
    parser.add_argument("--input", required=True, help="coverage-map JSON file")
    parser.add_argument(
        "--github-summary",
        action="store_true",
        help="append the rendered Markdown to GITHUB_STEP_SUMMARY",
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        payload = parse_coverage_map(Path(args.input).read_text(encoding="utf-8"))
        summary = render_coverage_map_summary(payload)
    except (OSError, SummaryPayloadError) as error:
        print(f"intent-verify-summary: {error}", file=sys.stderr)
        return 2

    if not args.github_summary:
        print(summary, end="")
        return 0
    destination = os.environ.get("GITHUB_STEP_SUMMARY")
    if not destination:
        print("intent-verify-summary: GITHUB_STEP_SUMMARY is not set", file=sys.stderr)
        return 2
    try:
        with Path(destination).open("a", encoding="utf-8") as summary_file:
            summary_file.write(summary)
    except OSError as error:
        print(f"intent-verify-summary: {error}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
