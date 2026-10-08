import json
from src.bod_anchor import AnchorReceipt, LocalAnchorProvider

def test_local_anchor_is_idempotent(tmp_path):
    provider = LocalAnchorProvider(tmp_path / "anchors.json")
    commitment = "a" * 64
    first = provider.anchor(commitment)
    second = provider.anchor(commitment)
    assert first == second
    assert provider.verify(first)

def test_local_anchor_rejects_unknown_receipt(tmp_path):
    provider = LocalAnchorProvider(tmp_path / "anchors.json")
    receipt = AnchorReceipt("local", "b" * 64, "local:" + "b" * 64, "c" * 64)
    assert not provider.verify(receipt)