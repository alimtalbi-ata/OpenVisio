"""Regression for locked-layer double-click import. Author: Abdelhalim Talbi."""
import unittest
from openvisio.app import Editor
from openvisio.layers import project_visible

class LockedLayerImportRegression(unittest.TestCase):
    def test_editor_uses_project_visible_function(self):
        self.assertIs(Editor.add_node.__globals__["project_visible"], project_visible)

if __name__ == "__main__":
    unittest.main()
