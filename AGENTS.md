# AGENTS.md

## What this tool does

- Checks a markdown spec or intent document against a repo.
- Extracts acceptance items from the spec.
- Scans the repo for lexical evidence of those items.
- Returns one of: `verified`, `partial`, `missing`.

## When to use it

- Repo intent verification
- Spec drift checks
- Handoff verification
- CI guardrail before merge or release

## When not to use it

- Do not use it as proof of correctness.
- Do not use it when there is no markdown spec file.
- Do not use it when you need semantic analysis rather than lexical coverage.

## Minimal invocation

```bash
intent-verify check --spec INTENT.md --repo .
intent-verify check --spec SPEC.md --repo . --json
```

## Expected output shape

Text mode:

- one header line with spec path, repo path, files scanned
- one line per item with `OK`, `PART`, or `LOW`
- one summary verdict line

JSON mode:

- `spec_path`
- `repo_path`
- `files_scanned`
- `average_coverage`
- `verdict`
- `thresholds`
- `items[]`

## Known limitations

- lexical only
- may over-credit token overlap
- may under-credit different wording

## Common failure cases

- spec file path is wrong
- repo path is wrong
- thresholds are invalid
- spec language is too abstract for lexical matching

## What counts as success

- `verified` means every parsed item cleared the verified threshold
- `partial` means at least one item is only partly covered
- `missing` means at least one item fell below the minimum per-item threshold
