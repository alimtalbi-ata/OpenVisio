"""Headless undo/redo cleanup regressions. Author: Abdelhalim Talbi."""
import unittest
from unittest.mock import Mock
from openvisio.app import Editor

class HistoryCleanupTests(unittest.TestCase):
    def make_stub(self):
        class Stub:
            document = {"nodes": [], "edges": []}
            selected = "old"
            selected_edge = "edge"
            selected_nodes = {"old"}
            link_start = "old"
            _drag_anchor = (1, 2)
            _marquee_start = (3, 4)
            _marquee_end = (5, 6)
            status = Mock()
            draw = Mock()
        return Stub()

    def test_history_restore_clears_transient_interaction_state(self):
        stub = self.make_stub()
        new = {"nodes": [{"id": "restored"}], "edges": []}
        Editor._restore_history_document(stub, new, "Annulation")
        self.assertEqual(stub.document, new)
        self.assertIsNone(stub.selected)
        self.assertIsNone(stub.selected_edge)
        self.assertEqual(stub.selected_nodes, set())
        self.assertIsNone(stub.link_start)
        self.assertIsNone(stub._drag_anchor)
        self.assertIsNone(stub._marquee_start)
        self.assertIsNone(stub._marquee_end)
        stub.draw.assert_called_once()

    def test_no_history_keeps_document_and_explains(self):
        stub = self.make_stub()
        original = stub.document
        Editor._restore_history_document(stub, None, "Rétablissement")
        self.assertIs(stub.document, original)
        stub.draw.assert_not_called()
        stub.status.set.assert_called_once()
