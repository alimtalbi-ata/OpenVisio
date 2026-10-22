"""Dimension-aware boundary attachment for straight infrastructure links.

The attachment is computed independently for the source and target rectangles.
Legacy 140x60 diagrams retain their original geometry. Overlapping outlines
fall back to centres instead of reversing the connector. No Visio dynamic glue
fidelity is claimed. Author: Abdelhalim Talbi.
"""
from math import isfinite
from .node_geometry import node_half_sizes


def connector_endpoints(source, target, half_width=70.0, half_height=30.0):
    """Return two outline points on centre-to-centre ray, or centres if overlapping.

    Explicit half_width/half_height remain supported for legacy callers. Node
    width/height, when present, override these defaults independently.
    """
    ax, ay = float(source["x"]), float(source["y"])
    bx, by = float(target["x"]), float(target["y"])
    if not all(isfinite(v) for v in (ax, ay, bx, by, half_width, half_height)):
        raise ValueError("Géométrie de connecteur non finie")
    if half_width <= 0 or half_height <= 0:
        raise ValueError("Dimensions de forme invalides")
    shw, shh = node_half_sizes(source) if "width" in source or "height" in source else (half_width, half_height)
    thw, thh = node_half_sizes(target) if "width" in target or "height" in target else (half_width, half_height)
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (ax, ay), (bx, by)
    def fraction(hw, hh):
        values = []
        if dx:
            values.append(hw / abs(dx))
        if dy:
            values.append(hh / abs(dy))
        return min(values)
    first, last = fraction(shw, shh), fraction(thw, thh)
    if first + last >= 1:
        return (ax, ay), (bx, by)
    return (ax + dx * first, ay + dy * first), (bx - dx * last, by - dy * last)


def lane_endpoints(source, target, lane=0.0):
    """Shift each straight-link anchor *along* its equipment boundary."""
    start, end = connector_endpoints(source, target)
    if not lane:
        return start, end

    def tangent_shift(point, node):
        hw, hh = node_half_sizes(node)
        if abs(abs(point[0] - node['x']) - hw) < 1e-6:
            return point[0], point[1] + max(-hh + 1e-6, min(hh - 1e-6, lane))
        return point[0] + max(-hw + 1e-6, min(hw - 1e-6, lane)), point[1]

    return tangent_shift(start, source), tangent_shift(end, target)
