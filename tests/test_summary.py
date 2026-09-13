import json

import pytest

from intent_verify.summary import (
    SummaryPayloadError,
    parse_coverage_map,
    render_coverage_map_summary,
)


def coverage_map(**overrides):
    payload = {
        "schema_version": "intent-verify.coverage-map.v1",
        "signal_kind": "lexical_scope_coverage",
        "acceptance_authority": False,
        "spec_path": "AGENTS.md",
        "evidence_roots": ["src", "tests"],
        "files_scanned": 12,
        "average_coverage": 0.75,
        "verdict": "partial",
        "decision": "inspect",
        "items": [
            {
                "text": "Parses acceptance items",
                "coverage": 1.0,
                "verdict": "covered",
                "evidence_paths": ["src/intent_verify/parser.py"],
            },
            {
                "text": "Search behavior",
                "coverage": 0.5,
                "verdict": "partial",
                "evidence_paths": [],
            },
        ],
    }
    payload.update(overrides)
    return payload


def test_summary_renders_advisory_contract_counts_and_links():
    summary = render_coverage_map_summary(
        coverage_map(),
        {
            "GITHUB_REPOSITORY": "hermes-labs-ai/intent-verify",
            "GITHUB_SHA": "a" * 40,
            "GITHUB_RUN_ID": "12345",
        },
    )

    assert "PARTIAL · inspect" in summary
    assert "Acceptance authority remains `false`" in summary
    assert "Items: 1 covered, 1 partial, 0 gap." in summary
    assert "Package: `intent-verify " in summary
    assert "blob/" in summary
    assert "actions/runs/12345" in summary
    assert "Search behavior" in summary


def test_summary_escapes_and_bounds_untrusted_labels():
    hostile = "<tag>| **unsafe** `code` " + "x" * 300
    summary = render_coverage_map_summary(
        coverage_map(
            items=[
                {
                    "text": hostile,
                    "coverage": 0.5,
                    "verdict": "gap",
                    "evidence_paths": [],
                }
            ]
        ),
        {},
    )

    assert "&lt;tag&gt;\\| \\*\\*unsafe\\*\\* \\`code\\`" in summary
    assert hostile not in summary
    assert "…" in summary


@pytest.mark.parametrize(
    "payload",
    [
        "not json",
        json.dumps([]),
        json.dumps(coverage_map(acceptance_authority=True)),
        json.dumps(coverage_map(items=[{"text": "bad"}])),
    ],
)
def test_summary_rejects_malformed_or_authoritative_payloads(payload):
    with pytest.raises(SummaryPayloadError):
        parse_coverage_map(payload)


@pytest.mark.parametrize(
    "payload",
    [
        coverage_map(files_scanned=True),
        coverage_map(average_coverage=True),
        coverage_map(average_coverage=float("nan")),
        coverage_map(average_coverage=10**100),
        coverage_map(
            items=[
                {
                    "text": "Valid label",
                    "coverage": True,
                    "verdict": "covered",
                    "evidence_paths": [],
                }
            ]
        ),
        coverage_map(
            items=[
                {
                    "text": "Valid label",
                    "coverage": float("inf"),
                    "verdict": "covered",
                    "evidence_paths": [],
                }
            ]
        ),
    ],
)
def test_summary_rejects_boolean_non_finite_and_out_of_range_coverage(payload):
    with pytest.raises(SummaryPayloadError):
        parse_coverage_map(json.dumps(payload))
