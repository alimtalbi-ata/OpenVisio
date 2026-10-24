"""V42.91: editable FC multipath template, persistence and connector identity.

The synthetic topology is illustrative, not a discovery of real WWPNs.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from collections import Counter
from pathlib import Path

from openvisio.history import History
from openvisio.model import load, save, validate
from openvisio.parallel_geometry import display_edges
from openvisio.templates import TEMPLATES, create_template
from openvisio.vsdx import export_vsdx, import_vsdx


class MultipathTemplateTests(unittest.TestCase):
    def setUp(self):
        self.document = create_template("SAN multipath FC (2 fabrics)")

    def test_new_template_is_available_and_valid(self):
        self.assertIn("SAN multipath FC (2 fabrics)", TEMPLATES)
        self.assertEqual(validate(self.document), self.document)
        self.assertEqual(len(self.document["nodes"]), 5)
        self.assertEqual(len(self.document["edges"]), 12)
        self.assertEqual({layer["id"] for layer in self.document["layers"]},
                         {"fabric-a", "fabric-b"})

    def test_all_san_pairs_have_two_distinct_physical_paths(self):
        pairs = Counter((edge["from"], edge["to"]) for edge in self.document["edges"])
        self.assertEqual(sorted(pairs.values()), [2] * 6)
        self.assertTrue(all(edge["protocol"] == "FC" for edge in self.document["edges"]))
        for pair in pairs:
            edges = [e for e in self.document["edges"] if (e["from"], e["to"]) == pair]
            self.assertEqual(len({(e["source_port"], e["target_port"]) for e in edges}), 2)
            self.assertEqual({e["layer"] for e in edges},
                             {"fabric-" + e["fabric"].lower() for e in edges})
        rendered = display_edges(self.document["edges"], self.document["nodes"])
        self.assertEqual(len({e["id"] for e in rendered}), 12)
        self.assertTrue(all(e.get("_lane_offset") for e in rendered))

    def test_native_save_reopen_preserves_fabrics_ports_and_layers(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fabric.ovjson"
            save(path, self.document, require_absent=True)
            self.assertEqual(load(path), self.document)

    def test_vsdx_embedded_roundtrip_preserves_topology(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "fabric.vsdx"
            export_vsdx(path, self.document, require_absent=True)
            self.assertEqual(import_vsdx(path), self.document)

    def test_undo_redo_restores_deleted_fc_path(self):
        history = History(self.document)
        modified = {**self.document, "edges": self.document["edges"][:-1]}
        self.assertTrue(history.record(modified))
        self.assertEqual(len(history.undo()["edges"]), 12)
        self.assertEqual(len(history.redo()["edges"]), 11)

    def test_templates_are_isolated_from_mutation(self):
        original = self.document
        original["layers"][0]["name"] = "Changed"
        original["edges"][0]["source_port"] = "Changed"
        fresh = create_template("SAN multipath FC (2 fabrics)")
        self.assertEqual(fresh["layers"][0]["name"], "Fabric A")
        self.assertEqual(fresh["edges"][0]["source_port"], "hba0")
        self.assertTrue({n["id"] for n in original["nodes"]}.isdisjoint(
                        {n["id"] for n in fresh["nodes"]}))


if __name__ == "__main__":
    unittest.main()
