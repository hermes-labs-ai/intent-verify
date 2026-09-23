"""Native Hermes Agent tool contract using the existing Intent Verify fixtures."""

import json
from pathlib import Path

from intent_verify.hermes_agent import intent_verify_map, register

ROOT = Path(__file__).resolve().parents[1]


def test_registration_and_real_map_invocation():
    registered = {}

    class Context:
        def register_tool(self, **kwargs):
            registered.update(kwargs)

    register(Context())
    assert registered["name"] == "intent_verify_map"
    assert registered["toolset"] == "intent_verify"
    fixture = ROOT / "tests" / "fixtures" / "repo_ok"
    payload = json.loads(registered["handler"]({
        "spec_path": str(fixture / "INTENT.md"),
        "repo_path": str(fixture),
        "evidence_paths": ["src"],
    }))
    assert payload["verdict"] == "covered"
    assert payload["evidence_roots"] == ["src"]
    assert payload["acceptance_authority"] is False


def test_findings_are_returned_without_false_success():
    fixture = ROOT / "tests" / "fixtures" / "repo_docs_only"
    payload = json.loads(intent_verify_map({
        "spec_path": str(fixture / "INTENT.md"),
        "repo_path": str(fixture),
        "evidence_paths": ["src"],
    }))
    assert payload["verdict"] == "gap"
    assert payload["decision"] == "inspect"


def test_missing_explicit_paths_rejected():
    payload = json.loads(intent_verify_map({"spec_path": "x", "repo_path": "."}))
    assert "error" in payload
    assert payload["acceptance_authority"] is False
