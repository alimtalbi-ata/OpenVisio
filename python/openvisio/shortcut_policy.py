"""Keyboard shortcut focus policy. Author: Abdelhalim Talbi."""
TEXT_WIDGET_CLASSES = frozenset({"Entry", "Text", "Spinbox", "TEntry", "TCombobox"})

def editor_shortcut_allowed(widget_class, in_editor_window):
    """Keep native text editing and modal dialogs isolated from editor shortcuts."""
    return bool(in_editor_window) and widget_class not in TEXT_WIDGET_CLASSES
