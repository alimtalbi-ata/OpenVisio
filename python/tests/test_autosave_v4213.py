"""Recovery journal qualification. Author: Abdelhalim Talbi."""
import json
import tempfile
import unittest
from pathlib import Path

from openvisio.autosave import (
    RecoveryConflict, digest_file, discard_journal, journal_path,
    read_journal, write_journal,
)
from openvisio.model import load, save


class AutosaveTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / "fabric.ovjson"
        self.original = {"nodes": [{"id": "a", "x": 10, "y": 20}], "edges": []}
        self.edited = {"nodes": [{"id": "a", "x": 44, "y": 55}], "edges": []}
        save(self.path, self.original)
        self.base = digest_file(self.path)

    def test_recovery_preserves_original_and_backup(self):
        native = self.path.read_bytes()
        backup = self.path.with_name(self.path.name + ".bak")
        write_journal(self.path, self.edited, self.base)
        self.assertEqual(self.path.read_bytes(), native)
        self.assertFalse(backup.exists())
        self.assertEqual(read_journal(self.path), self.edited)
        discard_journal(self.path)
        self.assertIsNone(read_journal(self.path))
        self.assertEqual(load(self.path), self.original)

    def test_external_change_blocks_recovery_and_new_journal(self):
        write_journal(self.path, self.edited, self.base)
        save(self.path, {"nodes": [], "edges": []})
        with self.assertRaises(RecoveryConflict):
            read_journal(self.path)
        old = journal_path(self.path).read_bytes()
        with self.assertRaises(RecoveryConflict):
            write_journal(self.path, self.edited, self.base)
        self.assertEqual(journal_path(self.path).read_bytes(), old)

    def test_tampering_is_detected(self):
        write_journal(self.path, self.edited, self.base)
        data = json.loads(journal_path(self.path).read_text(encoding="utf-8"))
        data["document"]["nodes"][0]["x"] = 999
        journal_path(self.path).write_text(json.dumps(data), encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "altéré"):
            read_journal(self.path)

    def test_invalid_document_does_not_replace_journal(self):
        write_journal(self.path, self.edited, self.base)
        previous = journal_path(self.path).read_bytes()
        with self.assertRaises(ValueError):
            write_journal(self.path, {"nodes": [{"id": "bad", "x": float("nan"), "y": 0}], "edges": []}, self.base)
        self.assertEqual(journal_path(self.path).read_bytes(), previous)

    def test_oversized_and_malformed_journal_rejected(self):
        journal_path(self.path).write_text("not json", encoding="utf-8")
        with self.assertRaisesRegex(ValueError, "illisible"):
            read_journal(self.path)
        journal_path(self.path).write_bytes(b"a" * 20_000_001)
        with self.assertRaisesRegex(ValueError, "volumineux"):
            read_journal(self.path)

    def test_absent_journal_is_safe(self):
        self.assertIsNone(read_journal(self.path))
        discard_journal(self.path)


if __name__ == "__main__":
    unittest.main()
