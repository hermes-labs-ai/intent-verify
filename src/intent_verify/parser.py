from __future__ import annotations

import re

INLINE_RE = re.compile(r"(?:^|\n)\s*(Accepts?|Requirements?|Scope):\s*([^\n]+)", re.IGNORECASE)


def parse_spec_items(text: str, section: str | None = None) -> list[str]:
    items: list[str] = []
    items.extend(_parse_inline_items(text))
    items.extend(_parse_section_items(text, section))

    deduped: list[str] = []
    seen: set[str] = set()
    for item in items:
        cleaned = item.strip().strip(".")
        key = cleaned.casefold()
        if cleaned and key not in seen:
            seen.add(key)
            deduped.append(cleaned)
    return deduped


def _parse_inline_items(text: str) -> list[str]:
    items: list[str] = []
    for match in INLINE_RE.finditer(text):
        raw = match.group(2).strip()
        parts = [part.strip(" .\t") for part in re.split(r",\s*|\s*;\s*", raw) if part.strip()]
        items.extend(parts)
    return items


def _parse_section_items(text: str, section: str | None) -> list[str]:
    target_names = ["Accepts", "Requirements", "Scope"]
    if section:
        target_names = [section]
    pattern = "|".join(re.escape(name) for name in target_names)
    header_re = re.compile(
        rf"(?:^|\n)#+\s*({pattern})\s*\n(.+?)(?=\n#|\Z)",
        re.IGNORECASE | re.DOTALL,
    )
    items: list[str] = []
    for match in header_re.finditer(text):
        body = match.group(2)
        for line in body.splitlines():
            stripped = line.strip()
            if not stripped:
                continue
            bullet = re.match(r"^[-*+]\s+(.+)$", stripped)
            ordered = re.match(r"^\d+\.\s+(.+)$", stripped)
            if bullet:
                items.append(bullet.group(1).strip())
            elif ordered:
                items.append(ordered.group(1).strip())
    return items
