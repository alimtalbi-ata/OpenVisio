"""Regression: protected SAN group commands cannot mutate locked topology.

Synthetic diagram only; no claim of native Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import copy
import unittest

from openvisio.group_commands import group_selection, ungroup_selection, resize_group
from openvisio.history import History


class LockedGroupCommandsTests(unittest.TestCase):
    def setUp(self):
        self.doc = {
            "layers": [{"id": "locked", "name": "Fabric A", "locked": True},
                       {"id": "work", "name": "Working", "locked": False}],
            "nodes": [
                {"id": "fc1", "x": 0, "y": 0, "shape": "san-switch", "layer": "locked"},
                {"id": "fc2", "x": 100, "y": 0, "shape": "san-switch", "layer": "locked"},
                {"id": "g", "x": 250, "y": 0, "shape": "visio-group", "width": 180, "height": 120, "layer": "work"},
                {"id": "host", "x": 250, "y": 0, "shape": "server", "visio_group_parent": "g", "layer": "work"},
                {"id": "array", "x": 450, "y": 0, "shape": "storage", "layer": "work"},
            ],
            "edges": [{"id": "san", "from": "host", "to": "array", "layer": "locked"}],
        }

    def test_grouping_locked_equipment_is_rejected_without_mutation(self):
        before = copy.deepcopy(self.doc)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            group_selection(self.doc, ["fc1", "fc2"], ident="new")
        self.assertEqual(self.doc, before)

    def test_ungrouping_locked_group_is_rejected(self):
        document = copy.deepcopy(self.doc)
        document["nodes"] = [n for n in document["nodes"] if n["id"] not in ("fc1", "fc2")]
        document["edges"] = []
        for node in document["nodes"]:
            if node["id"] in ("g", "host"):
                node["layer"] = "locked"
        before = copy.deepcopy(document)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            ungroup_selection(document, ["g"])
        self.assertEqual(document, before)

    def test_resizing_locked_group_is_rejected(self):
        document = copy.deepcopy(self.doc)
        for node in document["nodes"]:
            if node["id"] in ("g", "host"):
                node["layer"] = "locked"
        before = copy.deepcopy(document)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            resize_group(document, "g", 240, 150)
        self.assertEqual(document, before)

    def test_resizing_unlocked_group_cannot_move_protected_link(self):
        before = copy.deepcopy(self.doc)
        with self.assertRaisesRegex(ValueError, "verrouillé"):
            resize_group(self.doc, "g", 240, 150)
        self.assertEqual(self.doc, before)

    def test_unprotected_resize_and_undo_redo_remain_functional(self):
        document = copy.deepcopy(self.doc)
        document["edges"][0]["layer"] = "work"
        history = History(document)
        edited = resize_group(document, "g", 240, 150)
        self.assertTrue(history.record(edited))
        self.assertEqual(history.undo(), document)
        self.assertEqual(history.redo(), edited)
        self.assertEqual(document["nodes"][2]["width"], 180)

    def test_unprotected_group_and_ungroup_remain_functional(self):
        document = copy.deepcopy(self.doc)
        document["edges"] = []
        # Select peers on an editable layer; no locked fabric content changes.
        document["nodes"].extend([
            {"id": "peer1", "x": 600, "y": 0, "shape": "server", "layer": "work"},
            {"id": "peer2", "x": 720, "y": 0, "shape": "server", "layer": "work"},
        ])
        grouped, ident = group_selection(document, ["peer1", "peer2"], ident="new")
        self.assertEqual(ident, "new")
        restored = ungroup_selection(grouped, [ident])
        self.assertEqual(restored, document)


if __name__ == "__main__":
    unittest.main()
