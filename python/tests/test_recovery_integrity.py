"""Atomic backup and graph integrity tests. Author: Abdelhalim Talbi."""
import json
import tempfile
import unittest
from pathlib import Path
from openvisio.model import save, load
from openvisio.validation import validate_document

class RecoveryAndIntegrityTests(unittest.TestCase):
    def test_overwrite_preserves_previous_version_and_valid_new_version(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "diagram.ovjson"
            old = {"nodes": [{"id": "old", "x": 0, "y": 0}], "edges": []}
            new = {"nodes": [{"id": "new", "x": 10, "y": 10}], "edges": []}
            save(target, old)
            self.assertFalse(Path(str(target) + ".bak").exists())
            save(target, new)
            self.assertEqual(load(target), new)
            self.assertEqual(load(str(target) + ".bak"), old)
            self.assertEqual(list(Path(tmp).glob("*.tmp")), [])

    def test_invalid_save_never_replaces_original(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "diagram.ovjson"
            old = {"nodes": [], "edges": []}
            save(target, old)
            with self.assertRaises(ValueError):
                save(target, {"nodes": [{"id": "x", "x": float("nan"), "y": 0}], "edges": []})
            self.assertEqual(load(target), old)

    def test_duplicate_directed_edges_rejected(self):
        document = {"nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}],
                    "edges": [{"id": "e1", "from": "a", "to": "b"},
                              {"id": "e2", "from": "a", "to": "b"}]}
        with self.assertRaisesRegex(ValueError, "dupliquée"):
            validate_document(document)

    def test_opposite_direction_is_distinct(self):
        document = {"nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 1, "y": 1}],
                    "edges": [{"id": "e1", "from": "a", "to": "b"},
                              {"id": "e2", "from": "b", "to": "a"}]}
        self.assertEqual(len(validate_document(document)["edges"]), 2)
