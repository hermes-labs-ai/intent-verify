from intent_verify.parser import parse_spec_items


def test_parse_inline_items():
    text = "Accepts: upload PDF invoices, retry provider timeout"
    assert parse_spec_items(text) == ["upload PDF invoices", "retry provider timeout"]


def test_parse_section_items():
    text = """
# Spec

## Accepts
- uploads PDF invoices
- retries provider timeout
"""
    assert parse_spec_items(text) == ["uploads PDF invoices", "retries provider timeout"]


def test_parse_custom_section():
    text = """
## Requirements
- writes audit log
"""
    assert parse_spec_items(text, section="Requirements") == ["writes audit log"]
