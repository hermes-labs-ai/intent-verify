import json
import re
from pathlib import Path

import tomllib

from intent_verify import __version__

ROOT = Path(__file__).resolve().parents[1]


def _project_version() -> str:
    pyproject = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    return pyproject["project"]["version"]


def test_release_version_surfaces_match():
    project_version = _project_version()
    assert __version__ == project_version

    citation = (ROOT / "CITATION.cff").read_text(encoding="utf-8")
    assert re.search(rf'^version: "{re.escape(project_version)}"$', citation, re.MULTILINE)

    changelog = (ROOT / "CHANGELOG.md").read_text(encoding="utf-8")
    assert re.search(
        rf"^## \[{re.escape(project_version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$",
        changelog,
        re.MULTILINE,
    )

    release_date = re.search(
        rf"^## \[{re.escape(project_version)}\] - (\d{{4}}-\d{{2}}-\d{{2}})$",
        changelog,
        re.MULTILINE,
    )
    assert release_date
    assert re.search(
        rf'^date-released: "{re.escape(release_date.group(1))}"$',
        citation,
        re.MULTILINE,
    )

    versioned_metadata = (
        "plugin.json",
        ".claude-plugin/plugin.json",
        "gemini-extension.json",
        "codemeta.json",
    )
    for relative_path in versioned_metadata:
        payload = json.loads((ROOT / relative_path).read_text(encoding="utf-8"))
        assert payload["version"] == project_version, relative_path

    codemeta = json.loads((ROOT / "codemeta.json").read_text(encoding="utf-8"))
    expected_url = f"https://pypi.org/project/intent-verify/{project_version}/"
    assert codemeta["url"] == expected_url
    assert expected_url in codemeta["identifier"]


def test_public_release_pins_use_project_version():
    project_version = _project_version()
    release_tag = f"v{project_version}"
    exact_pip_pin = f"intent-verify=={project_version}"

    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    llms = (ROOT / "llms.txt").read_text(encoding="utf-8")
    skill = (ROOT / "skills" / "intent-verify" / "SKILL.md").read_text(encoding="utf-8")

    assert f"hermes-labs-ai/intent-verify@{release_tag}" in readme
    for document in (readme, llms):
        assert f"--ref {release_tag}" in document
    assert readme.count(exact_pip_pin) >= 1
    assert skill.count(exact_pip_pin) >= 2
