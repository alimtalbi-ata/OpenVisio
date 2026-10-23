"""Document service round-trip and failure safety tests. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from openvisio.document_service import open_document, save_document, restore_previous

class DocumentServiceTests(unittest.TestCase):
    def test_round_trip_and_previous_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "architecture.ovjson"
            first = {"nodes": [], "edges": []}
            second = {"nodes": [{"id": "server", "x": 12, "y": 22}], "edges": []}
            self.assertEqual(save_document(path, first), str(path))
            self.assertEqual(open_document(path), first)
            save_document(path, second)
            self.assertEqual(open_document(path), second)
            self.assertEqual(restore_previous(path), first)

    def test_invalid_document_does_not_overwrite_saved_version(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "architecture.ovjson"
            valid = {"nodes": [], "edges": []}
            save_document(path, valid)
            with self.assertRaises(ValueError):
                save_document(path, {"nodes": [{"id": "broken", "x": None, "y": 1}], "edges": []})
            self.assertEqual(open_document(path), valid)
