# Contributing

Thanks for contributing.

## Before opening a PR

- keep the tool narrow
- do not expand it into semantic verification
- prefer simple, deterministic behavior over clever heuristics
- update tests with any behavior change
- update `README.md`, `AGENTS.md`, and `llms.txt` if the CLI contract changes

## Local setup

```bash
python3 -m venv .venv
. .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e ".[dev]"
```

## Local checks

```bash
ruff check .
pytest -q
python3 -m py_compile src/intent_verify/*.py
```

## PR expectations

- one logical change per PR
- behavior change explained in the PR description
- tests included or updated
- no private data, internal prompts, or environment-specific paths
