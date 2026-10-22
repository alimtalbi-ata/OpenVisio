"""V42.12: Visio 1-D connector Geometry in the connector's local coordinate frame.

The source of truth remains the computed OpenVisio route. This emits a sequence
of absolute MoveTo/LineTo rows rather than flattening elbows into a diagonal.
It does not claim dynamic Visio rerouting or Microsoft Visio round-trip parity.
Author: Abdelhalim Talbi.
"""
from math import hypot, isfinite

from .routing import route_points

PX_PER_IN = 96.0


def connector_polyline(edge, nodes, min_x, min_y, page_height, *, scene=None):
    """Return (begin, end, [(row_type, local_x, local_y), ...]) in inches.

    Page y-axis is upward; OpenVisio's is downward. The local x-axis follows
    the connector's Begin->End direction, local y is its left-hand normal.
    Geometry rows are in Visio shape-local inches, not page coordinates.
    """
    points = scene.route_points(edge) if scene is not None else route_points(edge, nodes)
    if len(points) < 2 or len(points) > 2048:
        raise ValueError("Géométrie de connecteur VSDX invalide")
    if any(not (isfinite(x) and isfinite(y)) for x, y in points):
        raise ValueError("Géométrie de connecteur VSDX non finie")
    page_points = [((x - min_x) / PX_PER_IN,
                    (page_height - (y - min_y)) / PX_PER_IN) for x, y in points]
    begin, end = page_points[0], page_points[-1]
    dx, dy = end[0] - begin[0], end[1] - begin[1]
    distance = hypot(dx, dy)
    if distance <= 1e-12:
        raise ValueError("Connecteur VSDX de longueur nulle")
    ux, uy = dx / distance, dy / distance
    rows = []
    for index, (x, y) in enumerate(page_points):
        rx, ry = x - begin[0], y - begin[1]
        local_x = rx * ux + ry * uy
        local_y = -rx * uy + ry * ux
        rows.append(("MoveTo" if index == 0 else "LineTo", local_x, local_y))
    return begin, end, rows
