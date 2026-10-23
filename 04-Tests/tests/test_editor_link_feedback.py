"""Headless connection interaction feedback regression. Author: Abdelhalim Talbi."""
import unittest
from unittest.mock import Mock
from openvisio.app import Editor

class ConnectionFeedbackTests(unittest.TestCase):
    def test_same_node_cancels_pending_link_without_mutating_document(self):
        class Stub:
            document = {"nodes": [{"id": "a", "x": 0, "y": 0}], "edges": []}
            link_start = "a"
            selected_nodes = {"a"}
            selected = "a"
            selected_edge = None
            viewport = Mock()
            status = Mock()
            draw = Mock()
            _record_change = Mock()
            node_at = lambda self, x, y: {"id": "a"}
            edge_at = lambda self, x, y: None
        stub = Stub()
        event = Mock(x=0, y=0, state=0)
        Editor.click(stub, event)
        self.assertIsNone(stub.link_start)
        self.assertEqual(stub.document["edges"], [])
        stub._record_change.assert_not_called()
        self.assertIn("annulée", stub.status.set.call_args.args[0])
