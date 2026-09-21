---
description: "Map markdown acceptance items to explicit source and test evidence roots (advisory only)"
argument-hint: "--spec <path> --repo <path> --evidence-path <path> [--evidence-path <path>]"
allowed-tools: ["Bash(intent-verify:*)", "Read", "Glob"]
---

# Map acceptance items to implementation evidence

Run `intent-verify map` once when the user supplies a markdown spec, a repository,
and one or more explicit evidence paths such as `src` and `tests`. The map emits
provenance JSON and has `acceptance_authority: false`: even a `covered` result
only supports review; it never authorizes acceptance, merge, release, or a
public effect.

1. Require `--spec`, `--repo`, and at least one `--evidence-path`. If anything
   is missing, ask for it. Do not infer roots from the whole repository.
2. Confirm the paths are inside the named repository before running the command.
3. Run exactly once, keeping every user-supplied argument single-quoted:

   ```bash
   intent-verify map --spec '<spec-path>' --repo '<repo-path>' --evidence-path '<source-or-test-path>'
   ```

   Repeat `--evidence-path '<path>'` only for roots the user named. For a
   literal single quote, use `'\''`.
4. Read the JSON verdict and report its evidence paths. `covered` means the
   chosen roots lexically cover the parsed items; `partial` and `gap` identify
   items that need inspection. Do not treat any verdict as behavioral proof.

If `intent-verify` is unavailable, say so and give the user the local install
command `python -m pip install 'intent-verify==0.2.1'`; do not install it unless
the user asks.
