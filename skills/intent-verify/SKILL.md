---
name: intent-verify
description: Check a markdown spec, INTENT.md, or handoff doc against a repository for lexical coverage, or map its acceptance items to explicit source and test evidence paths, using the intent-verify CLI. Trigger when the user asks whether a repo still covers its spec, wants a spec-drift or handoff check, or wants acceptance items mapped to evidence. Results are advisory lexical evidence, never acceptance authority.
---

intent-verify is a deterministic CLI that parses acceptance items from a
markdown spec and measures lexical evidence for them in a repository. It makes
no model calls and sends no network requests
(https://github.com/hermes-labs-ai/intent-verify). Its output is an advisory
signal: it never proves correctness and never authorizes acceptance, merge,
release, or publication.

1. Pick a runner. If `intent-verify --help` works, use the bare
   `intent-verify` command. Otherwise tell the user it is not installed and,
   with their agreement, use `uvx intent-verify==0.2.0` (zero-install, no PATH
   changes) or `python -m pip install 'intent-verify==0.2.0'`. Keep the exact
   version pin so neither fetches an unreviewed newer release, and keep using
   the runner you picked for the remaining steps.
2. Require explicit inputs. `check` needs `--spec` and `--repo`; `map` also
   needs at least one `--evidence-path` (for example `src` and `tests`). If
   anything is missing, ask for it. Do not guess a spec, do not infer evidence
   roots from the whole repository, and do not scan a broad home directory.
   Confirm the spec is a file and that evidence paths are inside the named
   repository.
3. Run exactly one command, keeping every user-supplied path or heading in
   single quotes (for a literal single quote use `'\''`):

   ```bash
   intent-verify check --spec '<spec-path>' --repo '<repo-path>'
   intent-verify map --spec '<spec-path>' --repo '<repo-path>' --evidence-path '<source-or-test-path>'
   ```

   Pass `--section '<heading>'` only when requested, `--json` on `check` only
   when machine-readable output is useful, and repeat `--evidence-path` only
   for roots the user named.
4. Report the verdict and the low-coverage items or evidence paths.
   - `check`: `verified` (exit 0), `partial` (exit 1), `missing` (exit 2).
   - `map`: `covered` (exit 0), `partial` (exit 1), `gap` (exit 2); the JSON
     carries `acceptance_authority: false`.

   Exit 1 and exit 2 are findings to inspect, not reasons to retry.

Constraints:
- `verified` and `covered` mean lexical coverage reached its thresholds; they
  permit review, not acceptance. Do not present any verdict as behavioral
  proof.
- Matching is lexical only: it can over-credit incidental token overlap and
  under-credit implementations that use different wording.
- Run it on demand only; do not install it as an always-on or per-turn hook.
