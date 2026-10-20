"""Headless deletion state regression. Author: Abdelhalim Talbi."""
import unittest
from unittest.mock import Mock
from openvisio.app import Editor

class DeleteCleanupTests(unittest.TestCase):
    def test_delete_clears_pending_link_and_selection(self):
        class Stub:
            document = {"nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 2, "y": 2}],
                        "edges": [{"id": "e", "from": "a", "to": "b"}]}
            selected_nodes = {"a"}
            selected = "a"
            selected_edge = None
            link_start = "a"
            status = Mock()
            _record_change = Mock()
            draw = Mock()
        stub = Stub()
        Editor.delete_selected(stub)
        self.assertEqual([n["id"] for n in stub.document["nodes"]], ["b"])
        self.assertEqual(stub.document["edges"], [])
        self.assertIsNone(stub.link_start)
        self.assertEqual(stub.selected_nodes, set())
        stub._record_change.assert_called_once()
        stub.draw.assert_called_once()
