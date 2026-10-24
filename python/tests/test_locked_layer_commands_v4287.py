"""Locked-layer integrity at the editing-command boundary. Author: Abdelhalim Talbi."""
import copy
import unittest

from openvisio.commands import connect_equipment, remove_selection
from openvisio.history import History


class LockedLayerCommandTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "layers": [{"id": "fabric", "name": "SAN", "visible": True, "locked": True}],
            "nodes": [
                {"id": "fc", "x": 0, "y": 0, "shape": "san-switch", "layer": "fabric"},
                {"id": "host", "x": 120, "y": 0, "shape": "server"},
                {"id": "array", "x": 240, "y": 0, "shape": "storage"},
            ],
            "edges": [
                {"id": "fc-link", "from": "fc", "to": "host"},
                {"id": "protected-link", "from": "host", "to": "array", "layer": "fabric"},
            ],
        }

    def test_locked_node_cannot_be_deleted(self):
        before = copy.deepcopy(self.doc)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            remove_selection(self.doc, ["fc"])
        self.assertEqual(self.doc, before)

    def test_locked_edge_cannot_be_deleted_directly(self):
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            remove_selection(self.doc, edge_id="protected-link")
        self.assertEqual(len(self.doc["edges"]), 2)

    def test_unlocked_node_cannot_delete_incident_protected_edge(self):
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            remove_selection(self.doc, ["host"])
        self.assertEqual(len(self.doc["nodes"]), 3)

    def test_unlocked_node_cannot_delete_edge_to_locked_endpoint(self):
        document = copy.deepcopy(self.doc)
        document["edges"] = [document["edges"][0]]
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            remove_selection(document, ["host"])
        self.assertEqual(len(document["edges"]), 1)

    def test_cannot_connect_to_locked_endpoint(self):
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            connect_equipment(self.doc, "fc", "array", ident="new")
        self.assertEqual(len(self.doc["edges"]), 2)

    def test_unrelated_unlocked_edit_and_undo_redo_still_work(self):
        document = copy.deepcopy(self.doc)
        document["edges"] = [document["edges"][0]]
        history = History(document)
        edited = connect_equipment(document, "host", "array", ident="safe")
        self.assertTrue(history.record(edited))
        self.assertEqual(len(history.undo()["edges"]), 1)
        self.assertEqual(len(history.redo()["edges"]), 2)
        deleted = remove_selection(edited, edge_id="safe")
        self.assertEqual(deleted, document)


if __name__ == "__main__":
    unittest.main()
