"""V42.8 contract: SAN dual fabrics must preserve two distinct links."""
import unittest
from openvisio.commands import connect_equipment

class ParallelSANContract(unittest.TestCase):
    def test_explicit_dual_fabric_links(self):
        doc = {"nodes": [{"id": "a", "x": 0, "y": 0},
                         {"id": "b", "x": 300, "y": 0}], "edges": []}
        doc = connect_equipment(doc, "a", "b", ident="fabric-a")
        doc = connect_equipment(doc, "a", "b", ident="fabric-b", parallel=True)
        self.assertEqual(len(doc["edges"]), 2)
        self.assertTrue(all(edge["parallel"] for edge in doc["edges"]))
