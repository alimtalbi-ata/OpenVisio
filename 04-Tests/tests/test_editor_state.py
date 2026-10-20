"""Presentation state regression tests. Author: Abdelhalim Talbi."""
import unittest
from openvisio.editor_state import document_dirty, document_summary

class EditorStateTests(unittest.TestCase):
    def setUp(self):
        self.document = {"nodes": [{"id": "a"}, {"id": "b"}], "edges": [{"id": "e"}]}

    def test_dirty_is_snapshot_comparison(self):
        self.assertFalse(document_dirty("same", "same"))
        self.assertTrue(document_dirty("changed", "saved"))

    def test_unsaved_document_with_multi_selection(self):
        summary = document_summary(self.document, {"a", "b"}, dirty=True)
        self.assertIn("Sans titre", summary)
        self.assertIn("Modifié", summary)
        self.assertIn("2 équipements", summary)
        self.assertIn("1 liaisons", summary)
        self.assertIn("2 équipement(s) sélectionné(s)", summary)

    def test_saved_document_with_link_selection(self):
        summary = document_summary(self.document, selected_edge="e", path="diagram.ovjson")
        self.assertIn("diagram.ovjson", summary)
        self.assertIn("Enregistré", summary)
        self.assertIn("1 liaison sélectionnée", summary)
