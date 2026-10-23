"""Tkinter integration tests for unsaved crash recovery. Abdelhalim Talbi."""
import os
import tempfile
import tkinter as tk
import unittest
from pathlib import Path
from unittest.mock import patch

from openvisio.app import Editor
from openvisio.unsaved_recovery import UntitledSession, recoverable_sessions


@unittest.skipUnless(os.environ.get("OPENVISIO_GUI_TESTS") == "1", "GUI test explicitly enabled under Xvfb/Windows")
class UntitledEditorIntegrationTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name) / "Recovery"
        self.factory = patch("openvisio.app.UntitledSession", side_effect=lambda: UntitledSession(self.root))
        self.factory.start()
        self.addCleanup(self.factory.stop)
        self.recover = patch("openvisio.app.recoverable_sessions", side_effect=lambda: recoverable_sessions(self.root))
        self.recover.start()
        self.addCleanup(self.recover.stop)
        self.editor = Editor()
        self.addCleanup(self._cleanup_editor)

    def _cleanup_editor(self):
        try:
            self.editor._untitled_session.close()
            self.editor.destroy()
        except (tk.TclError, AttributeError):
            pass

    def test_autosave_new_diagram_then_recover_after_crash(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        self.assertTrue(journal.exists())
        self.editor._untitled_session.close()  # Emulates terminated process.
        with patch("openvisio.app.messagebox.askyesnocancel", return_value=True):
            new_editor = Editor()
            try:
                new_editor._offer_untitled_recovery()
                self.assertEqual(len(new_editor.document["nodes"]), 1)
                self.assertIsNone(new_editor.current_path)
                self.assertTrue(new_editor._untitled_session.path.exists())
                self.assertFalse(journal.exists())
            finally:
                new_editor._untitled_session.discard()
                new_editor._untitled_session.close()
                new_editor.destroy()

    def test_cancel_keeps_journal(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        self.editor._untitled_session.close()
        with patch("openvisio.app.messagebox.askyesnocancel", return_value=None):
            another = Editor()
            try:
                another._offer_untitled_recovery()
                self.assertTrue(journal.exists())
            finally:
                another._untitled_session.close()
                another.destroy()

    def test_startup_recovery_does_not_replace_new_edits(self):
        stale = UntitledSession(self.root)
        stale.write({"nodes": [{"id": "old", "x": 1, "y": 1}], "edges": []})
        stale.close()
        self.editor.create_node(10, 20)
        with patch("openvisio.app.messagebox.askyesnocancel") as prompt:
            self.editor._offer_untitled_recovery()
            prompt.assert_not_called()
        self.assertNotEqual(self.editor.document["nodes"][0]["id"], "old")
        self.assertTrue(stale.path.exists())

    def test_clean_document_close_removes_stale_journal(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        self.editor.undo()
        self.assertEqual(self.editor._snapshot(), self.editor.saved_snapshot)
        self.assertTrue(self.editor._confirm_discard())
        self.assertFalse(journal.exists())

    def test_save_as_clears_untitled_journal(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        destination = str(Path(self.tmp.name) / "saved.ovjson")
        with patch("openvisio.app.filedialog.asksaveasfilename", return_value=destination):
            self.editor.store_as()
        self.assertTrue(Path(destination).is_file())
        self.assertFalse(journal.exists())
        self.assertEqual(self.editor.current_path, destination)

    def test_failed_save_preserves_recovery_journal(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        with patch("openvisio.app.filedialog.asksaveasfilename", return_value=str(self.root / "bad" / "file.ovjson")), \
             patch("openvisio.app.save_document_with_revision", side_effect=OSError("simulated disk error")), \
             patch("openvisio.app.messagebox.showerror"):
            self.editor.store_as()
        self.assertTrue(journal.exists())
        self.assertIsNone(self.editor.current_path)

    def test_discard_clears_untitled_journal(self):
        self.editor.create_node(10, 20)
        self.editor._autosave_tick()
        journal = self.editor._untitled_session.path
        with patch("openvisio.app.messagebox.askyesnocancel", return_value=False):
            self.assertTrue(self.editor._confirm_discard())
        self.assertFalse(journal.exists())


if __name__ == "__main__":
    unittest.main()
