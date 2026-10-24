"""Regression tests for menu placement and double-click safety."""
import unittest
from types import SimpleNamespace
from openvisio.app import Editor

class RealEditorInteractions(unittest.TestCase):
    def test_equipment_menu_does_not_stack_nodes(self):
        app = Editor()
        try:
            app.update()
            app._place_kind_center("storage")
            app._place_kind_center("san-switch")
            self.assertEqual(len(app.document["nodes"]), 2)
            a, b = app.document["nodes"]
            self.assertNotEqual((a["x"], a["y"]), (b["x"], b["y"]))
        finally:
            app.destroy()

    def test_double_click_existing_node_no_duplicate(self):
        app = Editor()
        try:
            app.update()
            app.create_node(200, 150)
            x, y = app.viewport.screen(200, 150)
            app.add_node(SimpleNamespace(x=x, y=y))
            self.assertEqual(len(app.document["nodes"]), 1)
        finally:
            app.destroy()
