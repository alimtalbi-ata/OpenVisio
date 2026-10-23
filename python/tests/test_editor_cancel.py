"""Headless regression for canceling a pending connection. Author: Abdelhalim Talbi."""
import unittest
from unittest.mock import Mock
from openvisio.app import Editor

class CancelInteractionTests(unittest.TestCase):
    def test_escape_clears_selection_and_pending_link(self):
        class EditorStub:
            selected_nodes = {"a", "b"}
            selected = "a"
            selected_edge = "edge"
            link_start = "a"
            status = Mock()
            draw = Mock()
        stub = EditorStub()
        Editor.clear_selection(stub)
        self.assertEqual(stub.selected_nodes, set())
        self.assertIsNone(stub.selected)
        self.assertIsNone(stub.selected_edge)
        self.assertIsNone(stub.link_start)
        stub.draw.assert_called_once_with()
        stub.status.set.assert_called_once()
