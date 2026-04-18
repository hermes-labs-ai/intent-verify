import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def run_cli(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "intent_verify.cli", *args],
        cwd=ROOT,
        env={"PYTHONPATH": str(ROOT / "src")},
        capture_output=True,
        text=True,
        check=False,
    )


def test_cli_verified_fixture():
    fixture = ROOT / "tests" / "fixtures" / "repo_ok"
    result = run_cli("check", "--spec", str(fixture / "INTENT.md"), "--repo", str(fixture))
    assert result.returncode == 0
    assert "VERIFIED" in result.stdout


def test_cli_partial_fixture_json():
    fixture = ROOT / "tests" / "fixtures" / "repo_partial"
    result = run_cli(
        "check",
        "--spec",
        str(fixture / "INTENT.md"),
        "--repo",
        str(fixture),
        "--json",
    )
    assert result.returncode == 1
    payload = json.loads(result.stdout)
    assert payload["verdict"] == "partial"


def test_cli_missing_fixture():
    fixture = ROOT / "tests" / "fixtures" / "repo_missing"
    result = run_cli("check", "--spec", str(fixture / "INTENT.md"), "--repo", str(fixture))
    assert result.returncode == 2
    assert "MISSING" in result.stdout
