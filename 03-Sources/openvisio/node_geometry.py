"""Shared node bounds for diagrams. Author: Abdelhalim Talbi."""
from math import isfinite

DEFAULT_WIDTH = 140.0
DEFAULT_HEIGHT = 60.0
MIN_SIZE = 4.0
MAX_SIZE = 20_000.0

def checked_size(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Dimension {field} invalide")
    if not isfinite(value) or not MIN_SIZE <= value <= MAX_SIZE:
        raise ValueError(f"Dimension {field} hors limites ({MIN_SIZE:g}..{MAX_SIZE:g} px)")
    return float(value)

def node_dimensions(node):
    return (checked_size(node.get("width", DEFAULT_WIDTH), "width"),
            checked_size(node.get("height", DEFAULT_HEIGHT), "height"))

def node_half_sizes(node):
    width, height = node_dimensions(node)
    return width / 2, height / 2

def node_bounds(node, padding=0.0):
    hw, hh = node_half_sizes(node)
    x, y = node["x"], node["y"]
    return x - hw - padding, y - hh - padding, x + hw + padding, y + hh + padding
