"""GUI integration: saved document journals must be isolated. Abdelhalim Talbi."""
import os
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from openvisio.app import Editor
from openvisio.autosave import digest_file, journal_path, write_journal
from openvisio.model import load, save


@unittest.skipUnless(os.environ.get("OPENVISIO_GUI_TESTS") == "1", "Requires real Tk display")
class SavedRecoveryEditorTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / "diagram.ovjson"
        self.base = {"nodes": [{"id": "base", "x": 1, "y": 1}], "edges": []}
        self.edited = {"nodes": [{"id": "edited", "x": 2, "y": 2}], "edges": []}
        save(self.path, self.base)
        self.editor = Editor()
        self.addCleanup(self._cleanup)

    def _cleanup(self):
        if self.editor._untitled_session:
            self.editor._untitled_session.discard()
            self.editor._untitled_session.close()
        self.editor.destroy()

    def test_save_does_not_discard_another_editors_pending_recovery(self):
        foreign = "b" * 32
        write_journal(self.path, self.edited, digest_file(self.path), session_id=foreign)
        self.editor.current_path = str(self.path)
        self.editor._saved_disk_digest = digest_file(self.path)
        self.editor.document = self.base
        self.editor.store()
        self.assertTrue(journal_path(self.path, foreign).exists())
        self.assertEqual(load(self.path), self.base)

    def test_open_can_restore_other_session_without_erasing_its_journal(self):
        foreign = "b" * 32
        write_journal(self.path, self.edited, digest_file(self.path), session_id=foreign)
        with patch("openvisio.app.filedialog.askopenfilename", return_value=str(self.path)), \
             patch("openvisio.app.messagebox.askyesnocancel", return_value=True):
            self.editor.open()
        self.assertEqual(self.editor.document, self.edited)
        self.assertEqual(load(self.path), self.base)
        self.assertTrue(journal_path(self.path, foreign).exists())

    def test_save_as_does_not_discard_existing_destination_recovery(self):
        foreign = "b" * 32
        write_journal(self.path, self.edited, digest_file(self.path), session_id=foreign)
        self.editor.document = self.base
        with patch("openvisio.app.filedialog.asksaveasfilename", return_value=str(self.path)), \
             patch("openvisio.app.messagebox.askyesno", return_value=True):
            self.editor.store_as()
        self.assertTrue(journal_path(self.path, foreign).exists())


if __name__ == "__main__":
    unittest.main()
