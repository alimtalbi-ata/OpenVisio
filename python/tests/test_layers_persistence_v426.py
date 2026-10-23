"""Regression: no data loss when saving and editing documents with layers."""
import tempfile
import unittest
from pathlib import Path
from openvisio.model import save, load, validate
from openvisio.history import History
from openvisio.commands import add_equipment


class LayerPersistenceTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "nodes": [{"id": "srv", "x": 20, "y": 30, "layer": "compute", "label": "SRV"}],
            "edges": [],
            "layers": [{"id": "compute", "name": "Compute", "visible": True, "locked": False}],
            "metadata": {"author": "Abdelhalim Talbi", "revision": 3},
            "extension": {"vendor": "OpenVisio", "future": [1, 2, 3]},
        }

    def test_save_load_is_lossless(self):
        with tempfile.TemporaryDirectory() as directory:
            target = Path(directory) / "layered.ovjson"
            save(target, self.doc)
            self.assertEqual(load(target), self.doc)

    def test_history_preserves_layers_and_metadata(self):
        history = History(self.doc)
        updated, _ = add_equipment(self.doc, 200, 150, ident="srv2")
        self.assertTrue(history.record(updated))
        self.assertEqual(history.undo(), self.doc)
        self.assertEqual(history.redo(), updated)

    def test_invalid_layer_reference_rejected(self):
        self.doc["nodes"][0]["layer"] = "missing"
        with self.assertRaisesRegex(ValueError, "Calque"):
            validate(self.doc)

    def test_duplicate_layers_rejected(self):
        self.doc["layers"].append({"id": "compute", "name": "duplicate"})
        with self.assertRaisesRegex(ValueError, "dupliqué"):
            validate(self.doc)

    def test_invalid_layer_flags_rejected(self):
        self.doc["layers"][0]["visible"] = "yes"
        with self.assertRaisesRegex(ValueError, "État de calque"):
            validate(self.doc)

    def test_metadata_type_rejected(self):
        self.doc["metadata"] = []
        with self.assertRaisesRegex(ValueError, "Métadonnées"):
            validate(self.doc)


if __name__ == "__main__":
    unittest.main()
