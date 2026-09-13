---
description: "Check a markdown spec against a repository for lexical coverage (advisory only)"
argument-hint: "--spec <path> --repo <path> [--section <heading>] [--json]"
allowed-tools: ["Bash(intent-verify:*)", "Read", "Glob"]
---

# Check repository intent coverage

Run `intent-verify check` once for the explicit markdown spec and repository the
user names. This is an on-demand lexical coverage signal; it never proves
correctness or authorizes acceptance, merge, release, or publication.

1. If either `--spec` or `--repo` is missing, ask for it. Do not guess a spec
   and do not scan a broad home directory.
2. Confirm the named spec is a file and the repository is the intended scope.
3. Run exactly one command with the resolved paths as single shell arguments:

   ```bash
   intent-verify check --spec '<spec-path>' --repo '<repo-path>'
   ```

   Pass `--section '<heading>'` only when requested, and `--json` only when
   machine-readable output is useful. Keep every user-supplied path or heading
   in single quotes; for a literal single quote use `'\''`.
4. Report the verdict and the low-coverage items. `verified` means lexical
   coverage reached its configured thresholds, not that the change is correct.
   Exit 1 (`partial`) and exit 2 (`missing`) are findings to inspect, not
   reasons to retry.

If `intent-verify` is unavailable, say so and give the user the local install
command `python -m pip install 'intent-verify>=0.2.0'`; do not install it unless
the user asks.
