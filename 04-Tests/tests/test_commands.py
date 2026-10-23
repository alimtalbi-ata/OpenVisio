"""Regression tests for GUI-independent editing commands."""
import unittest
from copy import deepcopy
from openvisio.commands import add_equipment, remove_selection, connect_equipment

class EditingCommandsTests(unittest.TestCase):
    def setUp(self):
        self.empty = {"nodes": [], "edges": []}

    def test_add_does_not_mutate_source(self):
        result, ident = add_equipment(self.empty, 10.4, 20.8, "server", ident="a")
        self.assertEqual(self.empty, {"nodes": [], "edges": []})
        self.assertEqual(result["nodes"][0]["id"], ident)
        self.assertEqual((result["nodes"][0]["x"], result["nodes"][0]["y"]), (10, 21))

    def test_reject_unknown_equipment(self):
        with self.assertRaises(ValueError):
            add_equipment(self.empty, 0, 0, "not-a-shape")

    def test_connect_and_cascade_delete(self):
        a, _ = add_equipment(self.empty, 0, 0, ident="a")
        b, _ = add_equipment(a, 100, 0, ident="b")
        original = deepcopy(b)
        linked = connect_equipment(b, "a", "b", ident="ab")
        self.assertEqual(b, original)
        self.assertEqual(len(linked["edges"]), 1)
        cleaned = remove_selection(linked, {"a"})
        self.assertEqual([n["id"] for n in cleaned["nodes"]], ["b"])
        self.assertEqual(cleaned["edges"], [])
        self.assertEqual(len(linked["edges"]), 1)

    def test_parallel_links_allowed_but_self_link_rejected(self):
        a, _ = add_equipment(self.empty, 0, 0, ident="a")
        b, _ = add_equipment(a, 10, 0, ident="b")
        linked = connect_equipment(b, "a", "b")
        parallel = connect_equipment(linked, "a", "b")
        self.assertEqual(len(parallel["edges"]), 2)
        self.assertNotEqual(parallel["edges"][0]["id"], parallel["edges"][1]["id"])
        with self.assertRaises(ValueError):
            connect_equipment(linked, "a", "a")
        with self.assertRaises(ValueError):
            connect_equipment(linked, "a", "missing")
