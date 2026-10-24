"""Regression: layers and VSDX metadata must survive validation and JSON roundtrip."""
import tempfile
import unittest
from pathlib import Path
from openvisio.model import validate, save, load
from openvisio.layers import create_layer, assign_nodes, project_visible

class LayerPersistenceTests(unittest.TestCase):
    def test_layers_survive_save_and_reload(self):
        doc = {"nodes": [{"id": "n1", "x": 10, "y": 20, "shape": "server"}], "edges": []}
        doc, lid = create_layer(doc, "Production")
        doc = assign_nodes(doc, ["n1"], lid)
        doc["metadata"] = {"import_format": "VSDX", "page_count": 1}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "drawing.json"
            save(path, doc)
            loaded = load(path)
        self.assertEqual(loaded["layers"], doc["layers"])
        self.assertEqual(loaded["nodes"][0]["layer"], lid)
        self.assertEqual(loaded["metadata"], doc["metadata"])

    def test_reject_orphaned_layer_reference(self):
        with self.assertRaises(ValueError):
            validate({"nodes": [{"id": "n1", "x": 0, "y": 0, "layer": "missing"}], "edges": [], "layers": []})

    def test_orphaned_reference_without_layer_collection_is_rejected(self):
        doc = {"nodes": [{"id": "n1", "x": 0, "y": 0, "layer": "missing"}], "edges": []}
        with self.assertRaises(ValueError):
            validate(doc)

    def test_hidden_layer_excludes_nodes(self):
        doc = {"nodes": [{"id": "n1", "x": 0, "y": 0}], "edges": []}
        doc, lid = create_layer(doc, "Private")
        doc = assign_nodes(doc, ["n1"], lid)
        doc["layers"][0]["visible"] = False
        self.assertEqual(project_visible(doc)["nodes"], [])
