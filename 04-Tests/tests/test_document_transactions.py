"""Document replacement and undo regression. Author: Abdelhalim Talbi."""
import unittest
from openvisio.document_transactions import replace_document
from openvisio.history import History

class DocumentTransactionTests(unittest.TestCase):
    def test_restore_preserves_unsaved_document_for_undo(self):
        initial = {"nodes": [], "edges": []}
        unsaved = {"nodes": [{"id": "unsaved", "x": 0, "y": 0}], "edges": []}
        backup = {"nodes": [{"id": "backup", "x": 2, "y": 3}], "edges": []}
        history = History(initial)
        current = replace_document(history, unsaved, backup)
        self.assertEqual(current, backup)
        self.assertEqual(history.undo(), unsaved)
        self.assertEqual(history.undo(), initial)
        self.assertEqual(history.redo(), unsaved)
        self.assertEqual(history.redo(), backup)

    def test_replacement_is_not_aliased_to_caller(self):
        initial = {"nodes": [], "edges": []}
        incoming = {"nodes": [{"id": "a", "x": 1, "y": 2}], "edges": []}
        result = replace_document(History(initial), initial, incoming)
        incoming["nodes"][0]["x"] = 99
        self.assertEqual(result["nodes"][0]["x"], 1)
