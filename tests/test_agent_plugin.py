"""Tests for the cross-host Agent Plugin surface.

The repository root is one plugin with one canonical skill,
`skills/intent-verify/SKILL.md`, and one manifest per host format:

  plugin.json                        portable Agent Plugins 1.0.0 manifest (Codex CLI)
  .agents/plugins/marketplace.json   Codex repo marketplace, source "./"
  .claude-plugin/marketplace.json    Claude Code marketplace, source "."
  .claude-plugin/plugin.json         Claude Code plugin (skills/ + commands/)
  gemini-extension.json              Gemini CLI extension (skills/)

Every marketplace entry must resolve to the root, and no other SKILL.md may
exist anywhere in the tree. Live tests install into an isolated HOME and are
skipped when the host CLI is absent.
"""
from __future__ import annotations

import json
import os
import re
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent
PORTABLE_MANIFEST = ROOT / "plugin.json"
CODEX_MARKETPLACE = ROOT / ".agents" / "plugins" / "marketplace.json"
CLAUDE_MARKETPLACE = ROOT / ".claude-plugin" / "marketplace.json"
CLAUDE_MANIFEST = ROOT / ".claude-plugin" / "plugin.json"
GEMINI_MANIFEST = ROOT / "gemini-extension.json"
SKILL = ROOT / "skills" / "intent-verify" / "SKILL.md"
PYPROJECT = ROOT / "pyproject.toml"
SCHEMA_ID = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
NAME_PATTERN = re.compile(r"^(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?$")
PORTABLE_KEYS = {
    "$schema", "name", "version", "description", "author", "homepage",
    "repository", "license", "keywords", "extensions",
}
IGNORED_DIRS = {".git", ".venv", "node_modules", ".pytest_cache", ".ruff_cache"}


def _json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


def _pyproject_field(name: str) -> str:
    text = PYPROJECT.read_text(encoding="utf-8")
    match = re.search(rf'^{re.escape(name)}\s*=\s*"([^"]+)"', text, flags=re.MULTILINE)
    assert match, f"{name} not found in pyproject.toml"
    return match.group(1)


def _frontmatter(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    match = re.match(r"^---\n(.*?)\n---\n", text, flags=re.DOTALL)
    assert match, f"{path} has no frontmatter"
    fields = {}
    for line in match.group(1).splitlines():
        key, _, value = line.partition(":")
        fields[key.strip()] = value.strip()
    return fields


def test_portable_manifest_follows_agent_plugins_schema():
    manifest = _json(PORTABLE_MANIFEST)
    assert manifest["$schema"] == SCHEMA_ID
    assert NAME_PATTERN.match(manifest["name"]) and len(manifest["name"]) <= 64
    assert set(manifest) <= PORTABLE_KEYS, set(manifest) - PORTABLE_KEYS
    assert set(manifest.get("author", {})) <= {"name", "email", "url"}


def test_every_manifest_identity_matches_pyproject():
    name, version = _pyproject_field("name"), _pyproject_field("version")
    description = _pyproject_field("description")
    for path in (PORTABLE_MANIFEST, CLAUDE_MANIFEST, GEMINI_MANIFEST):
        manifest = _json(path)
        assert manifest["name"] == name, path
        assert manifest["version"] == version, path
        assert manifest["description"] == description, path
    portable, claude = _json(PORTABLE_MANIFEST), _json(CLAUDE_MANIFEST)
    for key in ("author", "homepage", "repository", "license"):
        assert portable[key] == claude[key], key


def test_marketplaces_resolve_to_the_repository_root():
    claude = _json(CLAUDE_MARKETPLACE)
    (claude_entry,) = claude["plugins"]
    assert claude["name"] == claude_entry["name"] == "intent-verify"
    assert (ROOT / claude_entry["source"]).resolve() == ROOT.resolve()

    codex = _json(CODEX_MARKETPLACE)
    (codex_entry,) = codex["plugins"]
    assert codex["name"] == codex_entry["name"] == "intent-verify"
    assert codex_entry["source"] == {"source": "local", "path": "./"}
    assert (ROOT / codex_entry["source"]["path"]).resolve() == ROOT.resolve()
    assert codex_entry["policy"]["installation"] in {"AVAILABLE", "INSTALLED_BY_DEFAULT"}
    assert codex_entry["policy"]["authentication"] in {"ON_INSTALL", "ON_USE"}


def test_exactly_one_canonical_skill_in_the_tree():
    found = [
        path for path in ROOT.rglob("SKILL.md")
        if not IGNORED_DIRS.intersection(path.relative_to(ROOT).parts)
    ]
    assert found == [SKILL], found
    meta = _frontmatter(SKILL)
    assert meta["name"] == "intent-verify" == SKILL.parent.name
    assert meta["description"]
    body = SKILL.read_text(encoding="utf-8")
    assert "acceptance authority" in body or "authorizes acceptance" in body
    assert f"intent-verify=={_pyproject_field('version')}" in body
    for extra in (ROOT / ".agents" / "skills", ROOT / ".claude" / "skills",
                  ROOT / ".gemini", ROOT / ".codex-plugin", ROOT / "integrations"):
        assert not extra.exists(), f"{extra} would be a second, driftable plugin surface"


def test_claude_commands_live_in_the_root_plugin():
    for command in ("check", "map"):
        assert (ROOT / "commands" / f"{command}.md").is_file()


def test_documented_gemini_install_pins_a_ref():
    """The documented install resolves the reviewed semantic release."""
    pattern = re.compile(r"gemini extensions install https://github\.com/hermes-labs-ai/intent-verify[^\n`]*")
    expected_ref = f"v{_pyproject_field('version')}"
    for doc in (ROOT / "README.md", ROOT / "llms.txt"):
        commands = pattern.findall(doc.read_text(encoding="utf-8"))
        assert commands, f"{doc.name} no longer documents the Gemini install"
        for command in commands:
            ref_pattern = rf"(?:^|\s)--ref(?:=|\s+){re.escape(expected_ref)}(?:\s|$)"
            assert re.search(ref_pattern, command), (
                f"{doc.name}: {command!r} must pass --ref {expected_ref}"
            )


def _package(tmp_path: Path) -> Path:
    """The tracked install surface, without local build or venv state."""
    pkg = tmp_path / "intent-verify"
    pkg.mkdir()
    for rel in ("plugin.json", "gemini-extension.json"):
        shutil.copy2(ROOT / rel, pkg / rel)
    for rel in (".agents", ".claude-plugin", "skills", "commands"):
        shutil.copytree(ROOT / rel, pkg / rel)
    return pkg


def _run(argv: list[str], env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(argv, capture_output=True, text=True, check=False, env=env, timeout=120)


@pytest.mark.skipif(shutil.which("codex") is None, reason="codex CLI not installed")
def test_codex_marketplace_install_reads_back_the_skill(tmp_path):
    pkg = _package(tmp_path)
    home = tmp_path / "home"
    (home / ".codex").mkdir(parents=True)
    env = {"HOME": str(home), "CODEX_HOME": str(home / ".codex"),
           "PATH": os.environ.get("PATH", "/usr/bin:/bin")}

    add = _run(["codex", "plugin", "marketplace", "add", str(pkg)], env)
    assert add.returncode == 0, f"{add.stdout}\n{add.stderr}"
    install = _run(["codex", "plugin", "add", "intent-verify@intent-verify"], env)
    assert install.returncode == 0, f"{install.stdout}\n{install.stderr}"

    listed = _run(["codex", "plugin", "list"], env)
    line = next((ln for ln in listed.stdout.splitlines()
                 if ln.startswith("intent-verify@intent-verify")), "")
    assert "installed, enabled" in line, listed.stdout
    cached = (home / ".codex" / "plugins" / "cache" / "intent-verify" / "intent-verify"
              / _pyproject_field("version") / "skills" / "intent-verify" / "SKILL.md")
    assert cached.read_bytes() == SKILL.read_bytes()


@pytest.mark.skipif(shutil.which("gemini") is None, reason="gemini CLI not installed")
def test_gemini_extension_install_discovers_the_skill(tmp_path):
    pkg = _package(tmp_path)
    home = tmp_path / "home"
    (home / ".gemini").mkdir(parents=True)
    # Listing is local, but the CLI refuses to start without an auth method.
    (home / ".gemini" / "settings.json").write_text(
        '{"security":{"auth":{"selectedType":"gemini-api-key"}}}', encoding="utf-8")
    env = {"HOME": str(home), "GEMINI_API_KEY": "placeholder-not-a-key",
           "PATH": os.environ.get("PATH", "/usr/bin:/bin")}

    install = _run(["gemini", "extensions", "install", str(pkg), "--consent"], env)
    assert install.returncode == 0, f"{install.stdout}\n{install.stderr}"
    skills = _run(["gemini", "skills", "list"], env)
    assert skills.returncode == 0, skills.stderr
    installed = (home / ".gemini" / "extensions" / "intent-verify"
                 / "skills" / "intent-verify" / "SKILL.md")
    listing = skills.stdout + skills.stderr  # some versions print the listing to stderr
    assert "intent-verify [Enabled]" in listing, listing
    assert installed.read_bytes() == SKILL.read_bytes()
