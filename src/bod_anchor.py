from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json
from pathlib import Path
from typing import Protocol

_DOMAIN = b"BOD-ANCHOR-RECORD-V0.1\0"

def _commit(value: dict) -> str:
    payload = json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()
    return hashlib.sha256(_DOMAIN + payload).hexdigest()

@dataclass(frozen=True)
class AnchorReceipt:
    provider: str
    commitment: str
    locator: str
    receipt_id: str

class AnchorProvider(Protocol):
    name: str
    def anchor(self, commitment: str) -> AnchorReceipt: ...
    def verify(self, receipt: AnchorReceipt) -> bool: ...

class LocalAnchorProvider:
    name = "local"
    def __init__(self, path: str | Path):
        self.path = Path(path)
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists(): self.path.write_text("{}\n", encoding="utf-8")

    def _load(self) -> dict[str, dict]:
        return json.loads(self.path.read_text(encoding="utf-8"))

    def anchor(self, commitment: str) -> AnchorReceipt:
        if len(commitment) != 64 or any(c not in "0123456789abcdef" for c in commitment):
            raise ValueError("commitment must be a lowercase SHA-256 hex digest")
        records = self._load()
        if commitment in records:
            item = records[commitment]
            return AnchorReceipt(**item)
        locator = f"local:{commitment}"
        base = {"provider": self.name, "commitment": commitment, "locator": locator}
        receipt = AnchorReceipt(**base, receipt_id=_commit(base))
        records[commitment] = {"provider": receipt.provider, "commitment": receipt.commitment, "locator": receipt.locator, "receipt_id": receipt.receipt_id}
        self.path.write_text(json.dumps(records, ensure_ascii=False, sort_keys=True, indent=2) + "\n", encoding="utf-8")
        return receipt

    def verify(self, receipt: AnchorReceipt) -> bool:
        records = self._load()
        item = records.get(receipt.commitment)
        if item is None: return False
        return item == {"provider": receipt.provider, "commitment": receipt.commitment, "locator": receipt.locator, "receipt_id": receipt.receipt_id} and receipt.receipt_id == _commit({"provider": receipt.provider, "commitment": receipt.commitment, "locator": receipt.locator})