import tempfile
import unittest
from pathlib import Path
from openvisio.layers import create_layer, assign_nodes, set_visibility, project_visible, project_editable
from openvisio.model import save, load
from openvisio.history import History


class LayerTests(unittest.TestCase):
    def setUp(self):
        self.doc = {"nodes": [{"id": "n1", "x": 0, "y": 0},
                              {"id": "n2", "x": 200, "y": 0}],
                    "edges": [{"id": "e1", "from": "n1", "to": "n2"}],
                    "metadata": {"client": "infrastructure"}}

    def test_hide_preserves_data_and_incident_links(self):
        doc, layer = create_layer(self.doc, "SAN")
        doc = assign_nodes(doc, {"n1"}, layer)
        hidden = set_visibility(doc, layer, False)
        view = project_visible(hidden)
        self.assertEqual([n["id"] for n in view["nodes"]], ["n2"])
        self.assertEqual(view["edges"], [])
        self.assertEqual(len(hidden["nodes"]), 2)
        self.assertEqual(len(hidden["edges"]), 1)
        self.assertEqual(len(project_visible(set_visibility(hidden, layer, True))["edges"]), 1)

    def test_save_load_preserves_layers_and_metadata(self):
        doc, layer = create_layer(self.doc, "Production")
        doc = assign_nodes(doc, {"n1"}, layer)
        doc = set_visibility(doc, layer, False)
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / "diagram.ov.json"
            save(p, doc)
            self.assertEqual(load(p), doc)

    def test_undo_restores_assignment_and_visibility(self):
        history = History(self.doc)
        doc, layer = create_layer(self.doc, "Applications")
        history.record(doc)
        doc = assign_nodes(doc, {"n1"}, layer)
        history.record(doc)
        doc = set_visibility(doc, layer, False)
        history.record(doc)
        self.assertTrue(history.undo()["layers"][0]["visible"])
        self.assertNotIn("layer", history.undo()["nodes"][0])
        self.assertEqual(history.redo()["nodes"][0]["layer"], layer)

    def test_locked_nodes_are_not_editable(self):
        doc, layer = create_layer(self.doc, "Sécurité")
        doc = assign_nodes(doc, {"n1"}, layer)
        doc["layers"][0]["locked"] = True
        self.assertEqual([n["id"] for n in project_editable(doc)["nodes"]], ["n2"])
        self.assertEqual(project_editable(doc)["edges"], [])
        self.assertEqual(len(project_visible(doc)["nodes"]), 2)

    def test_unknown_layer_and_node_rejected(self):
        doc, layer = create_layer(self.doc, "NFS")
        with self.assertRaises(ValueError):
            assign_nodes(doc, {"unknown"}, layer)
        with self.assertRaises(ValueError):
            assign_nodes(doc, {"n1"}, "missing")
        with self.assertRaises(ValueError):
            set_visibility(doc, "missing", True)

    def test_duplicate_layer_name_rejected(self):
        doc, _ = create_layer(self.doc, "Fabric A")
        with self.assertRaises(ValueError):
            create_layer(doc, " fabric a ")

    def test_link_layer_can_hide_edge_without_hiding_nodes(self):
        doc, layer = create_layer(self.doc, "Liaisons SAN")
        doc["edges"][0]["layer"] = layer
        hidden = set_visibility(doc, layer, False)
        self.assertEqual(len(project_visible(hidden)["nodes"]), 2)
        self.assertEqual(project_visible(hidden)["edges"], [])
        self.assertEqual(len(hidden["edges"]), 1)

    def test_validation_rejects_dangling_layer_reference(self):
        from openvisio.model import validate
        doc = {**self.doc, "nodes": [{**self.doc["nodes"][0], "layer": "unknown"}, self.doc["nodes"][1]]}
        with self.assertRaises(ValueError):
            validate(doc)

    def test_assign_none_clears_layer(self):
        doc, layer = create_layer(self.doc, "Storage")
        doc = assign_nodes(doc, {"n1"}, layer)
        cleared = assign_nodes(doc, {"n1"}, None)
        self.assertNotIn("layer", cleared["nodes"][0])
        self.assertEqual(len(cleared["layers"]), 1)

    def test_locked_layer_prevents_reassignment(self):
        doc, layer = create_layer(self.doc, "Production")
        doc = assign_nodes(doc, {"n1"}, layer)
        doc["layers"][0]["locked"] = True
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            assign_nodes(doc, {"n1"}, None)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            assign_nodes(doc, {"n2"}, layer)
        self.assertNotIn("layer", doc["nodes"][1])
