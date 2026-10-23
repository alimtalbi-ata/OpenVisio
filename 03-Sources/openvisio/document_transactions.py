"""Pure transaction boundary for reversible document replacement. Author: Abdelhalim Talbi."""
from copy import deepcopy
from .model import validate

def replace_document(history, current, replacement):
    """Record current edits before a validated replacement, preserving undo."""
    previous = deepcopy(validate(current))
    incoming = deepcopy(validate(replacement))
    history.record(previous)
    history.record(incoming)
    return incoming
