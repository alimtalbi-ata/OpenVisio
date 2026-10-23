"""V42.17 saved-document crash recovery isolation and migration regressions.

Author: Abdelhalim Talbi.
"""
import json
import tempfile
import unittest
from pathlib import Path

from openvisio.autosave import (digest_file, discard_journal, journal_path,
                               list_journals, read_journal, write_journal,
                               RecoveryConflict)
from openvisio.model import save


class SavedRecoveryIsolationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "network-diagram.ovjson"
        self.base = {"nodes": [{"id": "base", "x": 0, "y": 0}], "edges": []}
        save(self.path, self.base)
        self.digest = digest_file(self.path)
        self.a = "a" * 32
        self.b = "b" * 32
        self.doc_a = {"nodes": [{"id": "A", "x": 1, "y": 1}], "edges": []}
        self.doc_b = {"nodes": [{"id": "B", "x": 2, "y": 2}], "edges": []}

    def test_two_editors_preserve_independent_pending_work(self):
        write_journal(self.path, self.doc_a, self.digest, session_id=self.a)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.b)
        self.assertEqual(read_journal(self.path, session_id=self.a), self.doc_a)
        self.assertEqual(read_journal(self.path, session_id=self.b), self.doc_b)
        self.assertEqual({entry["session"] for entry in list_journals(self.path)[0]}, {self.a, self.b})
        self.assertEqual(list_journals(self.path)[1], [])

    def test_discard_one_editor_never_removes_another(self):
        write_journal(self.path, self.doc_a, self.digest, session_id=self.a)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.b)
        discard_journal(self.path, session_id=self.a)
        self.assertFalse(journal_path(self.path, self.a).exists())
        self.assertEqual(read_journal(self.path, session_id=self.b), self.doc_b)
        self.assertEqual(digest_file(self.path), self.digest)

    def test_legacy_journal_survives_new_editor_cleanup(self):
        write_journal(self.path, self.doc_a, self.digest)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.b)
        discard_journal(self.path, session_id=self.b)
        self.assertEqual(read_journal(self.path), self.doc_a)
        found, warnings = list_journals(self.path)
        self.assertEqual([entry["session"] for entry in found], [None])
        self.assertFalse(warnings)

    def test_corrupt_one_session_does_not_hide_other(self):
        write_journal(self.path, self.doc_a, self.digest, session_id=self.a)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.b)
        envelope = json.loads(journal_path(self.path, self.a).read_text(encoding="utf-8"))
        envelope["session"] = self.b
        journal_path(self.path, self.a).write_text(json.dumps(envelope), encoding="utf-8")
        found, warnings = list_journals(self.path)
        self.assertEqual([entry["session"] for entry in found], [self.b])
        self.assertEqual(len(warnings), 1)
        self.assertIn("Session du journal incohérente", warnings[0])

    def test_stale_base_rejected_for_all_sessions(self):
        write_journal(self.path, self.doc_a, self.digest, session_id=self.a)
        save(self.path, self.doc_b)
        with self.assertRaises(RecoveryConflict):
            read_journal(self.path, session_id=self.a)
        found, warnings = list_journals(self.path)
        self.assertEqual(found, [])
        self.assertEqual(len(warnings), 1)
        self.assertTrue(journal_path(self.path, self.a).exists())

    def test_reject_malformed_session_identifiers(self):
        for sid in ("../x", "a" * 31, "G" * 32, "a" * 33, 1, ""):
            with self.subTest(sid=sid), self.assertRaises(ValueError):
                journal_path(self.path, sid)
        self.assertEqual(list_journals(self.path, limit=1), ([], []))
        with self.assertRaises(ValueError):
            list_journals(self.path, limit=0)

    def test_session_overwrite_updates_only_its_own_version(self):
        write_journal(self.path, self.doc_a, self.digest, session_id=self.a)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.b)
        write_journal(self.path, self.doc_b, self.digest, session_id=self.a)
        self.assertEqual(read_journal(self.path, session_id=self.a), self.doc_b)
        self.assertEqual(read_journal(self.path, session_id=self.b), self.doc_b)
        self.assertEqual(len(list_journals(self.path)[0]), 2)


if __name__ == "__main__":
    unittest.main()
