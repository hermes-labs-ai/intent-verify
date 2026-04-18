from __future__ import annotations

import re

STOP_WORDS = {
    "a",
    "an",
    "and",
    "as",
    "at",
    "be",
    "but",
    "by",
    "for",
    "from",
    "has",
    "have",
    "in",
    "into",
    "is",
    "it",
    "its",
    "of",
    "on",
    "or",
    "that",
    "the",
    "this",
    "to",
    "via",
    "was",
    "were",
    "will",
    "with",
    "without",
}

TOKEN_RE = re.compile(r"[a-zA-Z][a-zA-Z0-9_-]{2,}")


def tokenize(text: str) -> list[str]:
    words = [word.lower() for word in TOKEN_RE.findall(text)]
    seen: set[str] = set()
    result: list[str] = []
    for word in words:
        if word in STOP_WORDS or word in seen:
            continue
        seen.add(word)
        result.append(word)
    return result
