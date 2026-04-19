# Security Policy

## Reporting a vulnerability

Please do not open a public issue for a suspected security problem.

Instead:

- email the maintainer directly
- include reproduction steps
- include impact assessment if known

I will acknowledge receipt and work on a fix before public disclosure.

## Scope

This project is a local CLI for repo intent verification. Relevant reports include:

- command injection risks
- path traversal issues
- unsafe file handling
- malformed-input crashes with security impact

Out of scope:

- false positives or false negatives in lexical matching, unless they create a security issue
