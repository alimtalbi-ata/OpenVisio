"""Keyboard focus safety policy without a graphical display."""
import unittest
from openvisio.shortcut_policy import editor_shortcut_allowed

class ShortcutPolicyTests(unittest.TestCase):
    def test_canvas_shortcuts_allowed(self):
        self.assertTrue(editor_shortcut_allowed("Canvas", True))

    def test_text_widgets_keep_native_shortcuts(self):
        for widget in ("Entry", "Text", "Spinbox", "TEntry", "TCombobox"):
            with self.subTest(widget=widget):
                self.assertFalse(editor_shortcut_allowed(widget, True))

    def test_modal_dialog_shortcuts_not_forwarded(self):
        self.assertFalse(editor_shortcut_allowed("Canvas", False))
