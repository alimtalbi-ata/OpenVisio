"""Compute public Visio page extents without clipping routed SAN geometry.

The geometry is derived; it never mutates the diagram or persisted edges.
Author: Abdelhalim Talbi.
"""
from .node_geometry import node_bounds
from .routing import routing_scene
from .parallel_geometry import display_edges
from .connector_labels import layout_connector_labels


def page_extent(nodes, edges, *, margin=70, minimum=(800, 600)):
    """Return (left, top, width, height, routing_scene) in document pixels.

    Include equipment bounds, *all* routed connector points and the layout
    envelopes of visible metadata labels.  Routing errors propagate instead
    of silently generating an incomplete VSDX page.
    """
    scene = routing_scene(nodes)
    boxes = [node_bounds(node) for node in nodes]
    for edge in display_edges(edges, nodes):
        boxes.extend((x, y, x, y) for x, y in scene.route_points(edge))
    labels = layout_connector_labels(nodes, edges, scene=scene)
    boxes.extend(label.bounds for label in labels.labels.values())
    left = min((box[0] for box in boxes), default=0) - margin
    top = min((box[1] for box in boxes), default=0) - margin
    right = max((box[2] for box in boxes), default=minimum[0]) + margin
    bottom = max((box[3] for box in boxes), default=minimum[1]) + margin
    return left, top, max(minimum[0], right-left), max(minimum[1], bottom-top), scene
