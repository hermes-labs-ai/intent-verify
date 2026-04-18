from intent_verify.tokenizer import tokenize


def test_tokenize_dedupes_and_drops_stop_words():
    assert tokenize("Accepts uploaded PDF invoices and invoices") == [
        "accepts",
        "uploaded",
        "pdf",
        "invoices",
    ]
