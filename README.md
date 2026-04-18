# intent-verify

`intent-verify` is a deterministic spec-coverage lint for repositories and agent handoffs.

It reads a markdown spec file, extracts acceptance items, scans a codebase for lexical evidence of those items, and returns one of three verdicts:

- `verified`
- `partial`
- `missing`

This is a guardrail, not proof of correctness. It answers “does the implementation visibly cover the stated scope?” not “is the software correct?”

## Why this exists

Teams often have an `INTENT.md`, `SPEC.md`, or handoff doc that says what a repo should do. The implementation drifts. Reviews catch some of it, but late and inconsistently.

`intent-verify` gives you a fast, cheap check you can run in CI or before handoff.

## Install

```bash
pip install intent-verify
```

For local development:

```bash
pip install -e ".[dev]"
```

## Usage

```bash
intent-verify check --spec INTENT.md --repo .
intent-verify check --spec SPEC.md --repo . --json
intent-verify check --spec docs/handoff.md --repo src --min-verified 0.75 --min-item 0.35
```

## What it parses

By default it extracts items from:

- inline lines such as `Accepts: upload PDF invoices, retry on timeout`
- markdown sections such as `## Accepts` with bullet items

It also supports custom headings:

```bash
intent-verify check --spec SPEC.md --section "Requirements"
```

## Example output

```text
intent-verify: INTENT.md vs . (12 files)
  [OK   100%] Accepts uploaded PDF invoices
  [PART  50%] Retries provider timeout
  [LOW   20%] Emits audit trail for rejected invoices
intent-verify: MISSING — 1/3 items below 35% (avg 57%)
```

JSON mode:

```bash
intent-verify check --spec INTENT.md --repo . --json
```

## Limitations

- Lexical, not semantic.
- Can over-credit token overlap.
- Can under-credit implementations expressed with different vocabulary.
- Best used as a CI guardrail or review hint, not as a substitute for tests and code review.

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
