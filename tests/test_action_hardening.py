import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
USES_PATTERN = re.compile(r"^\s*(?:- )?uses:\s*([^\s#]+)", re.MULTILINE)
IMMUTABLE_ACTION_PATTERN = re.compile(r"[^@]+@[0-9a-f]{40}")
HARDENED_ACTION_COMMIT = "88f241112218434bad24fe562cbf3bee0eab05ba"
PUBLIC_WORKFLOW_SURFACES = ("README.md", "examples/github-action.yml")


def _uses(path: Path) -> list[str]:
    return USES_PATTERN.findall(path.read_text())


def test_public_action_pins_third_party_actions_to_commits():
    refs = _uses(ROOT / "action.yml")
    assert refs
    assert all(IMMUTABLE_ACTION_PATTERN.fullmatch(ref) for ref in refs)


def test_copyable_workflows_pin_the_hardened_action_commit():
    expected = f"hermes-labs-ai/intent-verify@{HARDENED_ACTION_COMMIT}"
    for relative_path in PUBLIC_WORKFLOW_SURFACES:
        refs = _uses(ROOT / relative_path)
        assert expected in refs, relative_path
        assert all(IMMUTABLE_ACTION_PATTERN.fullmatch(ref) for ref in refs), relative_path
