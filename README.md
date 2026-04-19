# intent-verify: repo intent verification and spec drift checks

Find spec drift fast when your repo has an `INTENT.md`, `SPEC.md`, or handoff doc but nobody knows if the code still matches it.

`intent-verify` checks a markdown spec against a repo and returns `verified`, `partial`, or `missing` so you can catch repo intent drift before review, release, or handoff.

- "My repo has an `INTENT.md` but nobody knows if the code still matches it."
- "Reviews catch scope drift too late."
- "A handoff doc says one thing and the implementation says another."
- "I want a cheap CI check for spec drift before merge."
- "We need repo intent verification without inventing another full compliance system."

Fastest install:

```bash
pip install intent-verify
```

Fastest real usage:

```bash
intent-verify check --spec INTENT.md --repo .
```

Exact outcome:

```text
intent-verify: INTENT.md vs . (12 files)
  [OK   100%] uploads PDF invoices
  [PART  50%] retries provider timeout
  [LOW   20%] writes audit log for rejected invoices
intent-verify: MISSING — 1/3 items below 30% (avg 57%)
```

This is a guardrail, not proof of correctness. It answers “does the implementation visibly cover the stated scope?” not “is the software correct?”

## Install

```bash
pip install intent-verify
```

For local development:

```bash
pip install -e ".[dev]"
```

## Common search-intent use cases

- repo intent verification
- spec drift check
- handoff verification
- acceptance criteria drift detection
- CI check for markdown spec vs code

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

## Output

```text
intent-verify: INTENT.md vs . (12 files)
  [OK   100%] uploads PDF invoices
  [PART  50%] retries provider timeout
  [LOW   20%] writes audit log for rejected invoices
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

## When To Use It

- You keep project intent in markdown.
- You want a lightweight repo intent verification step in CI.
- You need a handoff verification check before merging or releasing.

## When Not To Use It

- You need semantic verification of behavior.
- You do not have any human-readable spec, intent, or requirements file.
- You want proof of correctness instead of a fast drift signal.

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
