"""Invalid layer references must never crash validation with TypeError."""
import unittest
from openvisio.model import validate

class LayerReferenceTypeTests(unittest.TestCase):
    def test_unhashable_node_layer_rejected(self):
        doc = {"nodes": [{"id": "n", "x": 1, "y": 2, "layer": ["prod"]}], "edges": [],
               "layers": [{"id": "prod", "name": "Production"}]}
        with self.assertRaises(ValueError):
            validate(doc)

    def test_unhashable_edge_layer_rejected(self):
        doc = {"nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 2, "y": 2}],
               "edges": [{"id": "e", "from": "a", "to": "b", "layer": {"id": "prod"}}],
               "layers": [{"id": "prod", "name": "Production"}]}
        with self.assertRaises(ValueError):
            validate(doc)
