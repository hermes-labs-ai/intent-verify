import json
import re
from pathlib import Path

import tomllib

from intent_verify import __version__

ROOT = Path(__file__).resolve().parents[1]


def test_release_version_surfaces_match():
    project_version = tomllib.loads((ROOT / "pyproject.toml").read_text())["project"]["version"]
    assert __version__ == project_version

    citation = (ROOT / "CITATION.cff").read_text()
    assert re.search(rf'^version: "{re.escape(project_version)}"$', citation, re.MULTILINE)

    changelog = (ROOT / "CHANGELOG.md").read_text()
    changelog_pattern = rf"^## \[{re.escape(project_version)}\] - \d{{4}}-\d{{2}}-\d{{2}}$"
    assert re.search(changelog_pattern, changelog, re.MULTILINE)

    versioned_metadata = (
        "plugin.json",
        ".claude-plugin/plugin.json",
        "gemini-extension.json",
        "codemeta.json",
    )
    for relative_path in versioned_metadata:
        payload = json.loads((ROOT / relative_path).read_text())
        assert payload["version"] == project_version, relative_path

    metadata = json.loads((ROOT / "codemeta.json").read_text())
    expected_url = f"https://pypi.org/project/intent-verify/{project_version}/"
    assert metadata["url"] == expected_url
    assert expected_url in metadata["identifier"]
