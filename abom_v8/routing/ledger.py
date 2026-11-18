"""Append-only, hash-chained placement ledger.

Every seat and vacate is recorded in the same shape for every model; no model
has a special entry type.  The chain makes edits to an already-copied ledger
detectable.  It does not stop someone who controls the whole ledger from
recomputing it end to end: anchoring the head hash somewhere you trust (a
signed commit, a published release) is what closes that gap.
"""
from __future__ import annotations

from dataclasses import dataclass
import hashlib
import json

from .provenance import canonical_json

GENESIS_HASH = "0" * 64
ACTIONS = ("seat", "vacate")


class LedgerError(ValueError):
    """The ledger failed verification or could not be parsed."""


def _entry_hash(seq: int, action: str, niche_id: str, model_id: str,
                provenance_digest: str | None, prev_hash: str) -> str:
    payload = {"seq": seq, "action": action, "niche_id": niche_id, "model_id": model_id,
               "provenance_digest": provenance_digest, "prev_hash": prev_hash}
    return hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()


@dataclass(frozen=True, slots=True)
class LedgerEntry:
    seq: int
    action: str
    niche_id: str
    model_id: str
    provenance_digest: str | None
    prev_hash: str
    entry_hash: str

    def recompute(self) -> str:
        return _entry_hash(self.seq, self.action, self.niche_id, self.model_id,
                           self.provenance_digest, self.prev_hash)


class PlacementLedger:
    def __init__(self) -> None:
        self._entries: list[LedgerEntry] = []

    @property
    def entries(self) -> tuple[LedgerEntry, ...]:
        return tuple(self._entries)

    @property
    def head(self) -> str:
        return self._entries[-1].entry_hash if self._entries else GENESIS_HASH

    def __len__(self) -> int:
        return len(self._entries)

    def append(self, action: str, niche_id: str, model_id: str,
               provenance_digest: str | None = None) -> LedgerEntry:
        if action not in ACTIONS:
            raise LedgerError(f"unknown ledger action: {action!r}")
        seq, prev = len(self._entries), self.head
        entry = LedgerEntry(seq, action, niche_id, model_id, provenance_digest, prev,
                            _entry_hash(seq, action, niche_id, model_id, provenance_digest, prev))
        self._entries.append(entry)
        return entry

    @staticmethod
    def check(entries: tuple[LedgerEntry, ...]) -> bool:
        prev = GENESIS_HASH
        for index, entry in enumerate(entries):
            if (entry.seq != index or entry.prev_hash != prev
                    or entry.action not in ACTIONS or entry.entry_hash != entry.recompute()):
                return False
            prev = entry.entry_hash
        return True

    def verify(self) -> bool:
        return self.check(self.entries)

    def to_jsonl(self) -> str:
        lines = [canonical_json({
            "seq": e.seq, "action": e.action, "niche_id": e.niche_id, "model_id": e.model_id,
            "provenance_digest": e.provenance_digest, "prev_hash": e.prev_hash,
            "entry_hash": e.entry_hash,
        }) for e in self._entries]
        return "\n".join(lines) + ("\n" if lines else "")

    @classmethod
    def from_jsonl(cls, text: str) -> "PlacementLedger":
        entries: list[LedgerEntry] = []
        for number, line in enumerate(text.splitlines(), start=1):
            if not line.strip():
                continue
            try:
                raw = json.loads(line)
                entries.append(LedgerEntry(
                    int(raw["seq"]), raw["action"], raw["niche_id"], raw["model_id"],
                    raw["provenance_digest"], raw["prev_hash"], raw["entry_hash"],
                ))
            except (ValueError, KeyError, TypeError) as exc:
                raise LedgerError(f"line {number}: malformed ledger entry") from exc
        if not cls.check(tuple(entries)):
            raise LedgerError("ledger chain verification failed")
        ledger = cls()
        ledger._entries = entries
        return ledger
