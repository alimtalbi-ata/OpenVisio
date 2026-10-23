"""Safe obstacle clearance policy for orthogonal SAN multipath lanes.

Display-only geometry: never changes equipment bounds or saved port metadata.
Author: Abdelhalim Talbi.
"""
from math import isfinite


def lane_clearance(lane_offset, maximum=12.0):
    """Return bounded extra clearance for a display-only orthogonal lane."""
    lane = float(lane_offset)
    if not isfinite(lane) or not isfinite(maximum) or maximum < 0:
        raise ValueError('Invalid lane clearance')
    return min(abs(lane) / 2.0, maximum)


def expanded_intermediate_bounds(node_id, bounds, source_id, target_id, extra):
    """Inflate only intermediate obstacles; keep attachment equipment exact."""
    if node_id in (source_id, target_id) or not extra:
        return bounds
    left, top, right, bottom = bounds
    return (left - extra, top - extra, right + extra, bottom + extra)
