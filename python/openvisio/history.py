"""Bounded, reversible diagram history with compact large snapshots.

Only trusted, validated document snapshots are decoded. History never writes
pickle or executes user-supplied code. Author: Abdelhalim Talbi.
"""
from copy import deepcopy
import json
import zlib

from .model import validate


class History:
    """Undo/redo with a count limit and an approximate byte budget.

    The current document remains a normal dict. Large historical snapshots are
    compressed, preventing 100 edits of a dense SAN topology from retaining
    100 fully expanded copies. One oversized undo/redo entry is retained to
    preserve the most recent reversal, even if it exceeds the soft budget.
    """

    def __init__(self, document, limit=100, max_bytes=64 * 1024 * 1024,
                 compression_threshold=16 * 1024):
        if isinstance(limit, bool) or not isinstance(limit, int) or limit < 1:
            raise ValueError("Limite d'historique invalide")
        if isinstance(max_bytes, bool) or not isinstance(max_bytes, int) or max_bytes < 1:
            raise ValueError("Budget mémoire d'historique invalide")
        if (isinstance(compression_threshold, bool)
                or not isinstance(compression_threshold, int)
                or compression_threshold < 0):
            raise ValueError("Seuil de compression invalide")
        self.limit = limit
        self.max_bytes = max_bytes
        self.compression_threshold = compression_threshold
        self.past = []
        self.future = []
        self.current = deepcopy(validate(document))

    def _pack(self, document):
        """Represent one trusted snapshot without sharing mutable references."""
        try:
            payload = json.dumps(document, ensure_ascii=False, allow_nan=False,
                                 separators=(",", ":")).encode("utf-8")
        except (TypeError, ValueError, UnicodeError):
            # Extension fields may not be JSON-compatible until saved. Preserve
            # the legacy in-memory behavior rather than losing undo state.
            return (False, deepcopy(document), len(repr(document).encode("utf-8")))
        if len(payload) >= self.compression_threshold:
            packed = zlib.compress(payload, level=1)
            return (True, packed, len(packed))
        return (False, deepcopy(document), len(payload))

    @staticmethod
    def _unpack(snapshot):
        compressed, payload, _ = snapshot
        return json.loads(zlib.decompress(payload)) if compressed else deepcopy(payload)

    @property
    def history_bytes(self):
        """Encoded payload bytes retained for undo and redo (not Python overhead)."""
        return sum(item[2] for item in self.past + self.future)

    def _trim(self):
        while len(self.past) > self.limit:
            self.past.pop(0)
        while len(self.future) > self.limit:
            self.future.pop(0)
        # Drop the farthest undo/redo states first; keep at least one reversal.
        while self.history_bytes > self.max_bytes and len(self.past) + len(self.future) > 1:
            if self.past and (not self.future or len(self.past) >= len(self.future)):
                self.past.pop(0)
            else:
                self.future.pop(0)

    def record(self, document):
        snapshot = deepcopy(validate(document))
        if snapshot == self.current:
            return False
        packed = self._pack(self.current)
        self.past.append(packed)
        self.current = snapshot
        self.future.clear()
        self._trim()
        return True

    def undo(self):
        if not self.past:
            return None
        new_current = self._unpack(self.past[-1])
        future_entry = self._pack(self.current)
        self.past.pop()
        self.future.append(future_entry)
        self.current = new_current
        self._trim()
        return deepcopy(self.current)

    def redo(self):
        if not self.future:
            return None
        new_current = self._unpack(self.future[-1])
        past_entry = self._pack(self.current)
        self.future.pop()
        self.past.append(past_entry)
        self.current = new_current
        self._trim()
        return deepcopy(self.current)

    def reset(self, document):
        snapshot = deepcopy(validate(document))
        self.past.clear()
        self.future.clear()
        self.current = snapshot
