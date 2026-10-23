"""Deterministic *display-only* separation of redundant SAN paths.

Lane geometry is derived from the validated document and never persisted as
fabricated port coordinates. Every consumer (Tk, hit testing, SVG, VSDX) must
use the same decorated edge view. Author: Abdelhalim Talbi.
"""
from collections import defaultdict
from .node_geometry import node_half_sizes


def display_edges(edges, nodes):
    """Return new edge dictionaries, with ephemeral offsets for parallel pairs.

    Stable ordering by edge ID avoids moving surviving paths when users reorder
    the JSON edge list. Adaptive spacing prevents anchors leaving small shapes.
    Both directions of the same physical pair share a lane group, so a SAN
    request/response or bidirectional pair cannot render as one invisible line.
    No metadata is mutated.
    """
    by_id = {node['id']: node for node in nodes}
    groups = defaultdict(list)
    for edge in edges:
        # Physical corridor is unordered: A->B and B->A occupy the same
        # screen-space path unless they receive distinct display lanes.
        groups[tuple(sorted((edge['from'], edge['to'])))].append(edge)
    offsets = {}
    for (source, target), group in groups.items():
        if len(group) < 2:
            continue
        half_sizes = (*node_half_sizes(by_id[source]), *node_half_sizes(by_id[target]))
        max_span = max(0.0, min(24.0, min(half_sizes) - 4.0))
        step = min(16.0, 2.0 * max_span / (len(group) - 1))
        for index, edge in enumerate(sorted(group, key=lambda item: item['id'])):
            offsets[edge['id']] = (index - (len(group) - 1) / 2) * step
    return [{**edge, '_lane_offset': offsets[edge['id']]} if edge['id'] in offsets
            else dict(edge) for edge in edges]
