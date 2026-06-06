# intent-verify

[![CI](https://github.com/hermes-labs-ai/intent-verify/actions/workflows/ci.yml/badge.svg)](https://github.com/hermes-labs-ai/intent-verify/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/intent-verify.svg)](https://pypi.org/project/intent-verify/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

intent-verify is a deterministic, zero-LLM command-line tool that checks whether a repo's source still lexically covers the acceptance items written in a markdown spec, `INTENT.md`, or handoff doc — and returns `verified`, `partial`, or `missing`.

Use it when your repo has an `INTENT.md`, `SPEC.md`, or handoff doc but nobody knows whether the code still matches it. It is a fast guardrail for catching spec drift before review, release, or handoff.

## How it works

intent-verify is intentionally simple and fully deterministic — no model, no network:

1. Parse acceptance items from the spec (inline `Accepts:`/`Requirements:`/`Scope:` lines and bullet/numbered lists under matching headings).
2. Tokenize each item, dropping common stop words.
3. For each item, compute the fraction of its tokens that appear as substrings somewhere in the repo's source files (the spec file itself is excluded from the evidence).
4. Score each item against two thresholds and roll up to a single verdict.

Coverage is a lexical token-overlap signal, not a semantic judgment.

## Install

```bash
pip install intent-verify
```

For local development:

```bash
pip install -e ".[dev]"
```

## 60-second quickstart

Given a spec like:

```markdown
# Intent

## Accepts
- uploads PDF invoices
- retries provider timeout
```

run:

```bash
intent-verify check --spec INTENT.md --repo .
```

You get a per-item breakdown and a single verdict:

```text
intent-verify: INTENT.md vs . (12 files)
  [OK   100%] uploads PDF invoices
  [PART  50%] retries provider timeout
  [LOW   20%] writes audit log for rejected invoices
intent-verify: MISSING — 1/3 items below 30% (avg 57%)
```

(The file count, percentages, and items above are illustrative — your numbers depend on your spec and repo.)

The exit code mirrors the verdict, so it drops straight into CI or a pre-commit hook:

| Verdict | Meaning | Exit code |
| --- | --- | --- |
| `verified` | every parsed item cleared the verified threshold | `0` |
| `partial` | at least one item is only partly covered | `1` |
| `missing` | at least one item fell below the per-item minimum | `2` |

![intent-verify preview](assets/preview.png)

## Usage

```bash
intent-verify check --spec INTENT.md --repo .
intent-verify check --spec SPEC.md --repo . --json
intent-verify check --spec docs/handoff.md --repo src --min-verified 0.75 --min-item 0.35
```

Flags:

- `--spec` — path to the markdown spec, intent, or handoff file (required).
- `--repo` — path to the repo or source tree to scan (required).
- `--section` — target a specific markdown heading, for example `Requirements`.
- `--json` — emit machine-readable JSON instead of text.
- `--min-verified` — coverage an item must clear to count as verified (default `0.7`).
- `--min-item` — minimum per-item coverage before an item is treated as missing (default `0.3`).

### What it parses

By default it extracts items from:

- inline lines such as `Accepts: upload PDF invoices, retry on timeout`
- markdown sections such as `## Accepts` with bullet or numbered items (`Accepts`, `Requirements`, `Scope` headings, or a custom one via `--section`)

### JSON output

```bash
intent-verify check --spec INTENT.md --repo . --json
```

The JSON object includes `spec_path`, `repo_path`, `files_scanned`, `average_coverage`, `verdict`, the `thresholds` used, and an `items[]` array with each item's parsed text, tokens, coverage, and verdict.

## Limitations / what it does NOT do

- **Lexical, not semantic.** It matches tokens as substrings; it does not understand meaning, control flow, or behavior.
- **It can over-credit.** A token appearing anywhere in any scanned file counts, even if it is in a comment, a string, or an unrelated context.
- **It can under-credit.** A correct implementation written with different vocabulary than the spec will score low.
- **It is not proof of correctness** and does not replace tests or code review. It answers "does the implementation visibly cover the stated scope?" — not "is the software correct?"
- **It needs a human-readable spec.** With no `INTENT.md`/`SPEC.md`/requirements/handoff file there is nothing to check against.
- **Source-file scope only.** It scans a fixed set of source extensions (Python, JS/TS, Go, Rust, shell, config, markdown, etc.) and skips common build/vendor directories.

## Development

```bash
ruff check .
python3 -m pytest -q
python3 -m py_compile src/intent_verify/*.py
```

## Repository layout

```text
src/intent_verify/
tests/
examples/
```

---

Part of the [Hermes Labs reliability stack](https://github.com/hermes-labs-ai). Complementary siblings, not duplicates: [rule-audit](https://github.com/hermes-labs-ai/rule-audit) analyzes logical contradictions in system prompts, and [lintlang](https://github.com/hermes-labs-ai/lintlang) lints agent-config structure — intent-verify instead checks spec-vs-code drift.

## About Hermes Labs

Hermes Labs is an independent AI-reliability lab building open-source tools that catch silent failure modes in production AI. More at [hermes-labs.ai](https://hermes-labs.ai).
