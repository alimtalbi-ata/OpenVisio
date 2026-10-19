"""Tests for pure selection behavior."""
import unittest
from openvisio.selection_state import select_node, select_rectangle, reconcile_selection

class SelectionStateTests(unittest.TestCase):
    def test_click_selects_single_node(self):
        self.assertEqual(select_node({"a"}, "b"), ({"b"}, "b"))

    def test_ctrl_click_toggles(self):
        self.assertEqual(select_node({"a"}, "b", ctrl=True), ({"a", "b"}, None))
        self.assertEqual(select_node({"a", "b"}, "b", ctrl=True), ({"a"}, None))

    def test_multiselection_click_preserves_group_for_drag(self):
        self.assertEqual(select_node({"a", "b"}, "a"), ({"a", "b"}, "a"))

    def test_marquee_additive_uses_original_selection(self):
        self.assertEqual(select_rectangle({"a"}, {"b"}, additive=True), {"a", "b"})
        self.assertEqual(select_rectangle({"a"}, {"b"}), {"b"})

    def test_reconcile_removes_deleted_ids(self):
        doc = {"nodes": [{"id": "a"}], "edges": [{"id": "e"}]}
        self.assertEqual(reconcile_selection(doc, {"a", "deleted"}, "deleted", "e"), ({"a"}, None, None))
