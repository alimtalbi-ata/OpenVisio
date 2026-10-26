"""Validated static VSDX route preservation with geometry-safe fallback.

Only the narrow public, formula-free orthogonal subset recognised by the
external VSDX importer is preserved. A route is active only while both endpoint
geometries match the imported snapshot and no current equipment rectangle is
crossed. Otherwise the normal obstacle-avoiding router recalculates it.
Author: Abdelhalim Talbi.
"""
from math import isfinite

from .node_geometry import checked_size, node_bounds

SCHEMA = 1
MAX_POINTS = 2048
MAX_COORDINATE = 10_000_000.0
EPSILON = 1e-3
_REQUIRED_KEYS = {"schema", "source", "target", "points"}


def _number(value, field):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"Coordonnée de route VSDX invalide : {field}")
    value = float(value)
    if not isfinite(value) or abs(value) > MAX_COORDINATE:
        raise ValueError(f"Coordonnée de route VSDX hors limites : {field}")
    return value


def node_route_signature(node):
    """Return the exact geometry snapshot used to invalidate a static route."""
    x = _number(node.get("x"), "node.x")
    y = _number(node.get("y"), "node.y")
    width = checked_size(node.get("width", 140.0), "width")
    height = checked_size(node.get("height", 60.0), "height")
    return [round(x, 3), round(y, 3), round(width, 3), round(height, 3)]


def validate_visio_route(record):
    """Validate and return a canonical copy of a static route record.

    The strict schema, point-count and numeric bounds are applied both when a
    JSON document is loaded and when route geometry is used by the renderer.
    """
    if not isinstance(record, dict) or set(record) != _REQUIRED_KEYS:
        raise ValueError("Enregistrement de route VSDX invalide")
    if type(record.get("schema")) is not int or record.get("schema") != SCHEMA:
        raise ValueError("Version de route VSDX non prise en charge")

    def signature(value, name):
        if not isinstance(value, (list, tuple)) or len(value) != 4:
            raise ValueError(f"Géométrie {name} de route VSDX invalide")
        x, y, width, height = (_number(v, f"{name}[{i}]") for i, v in enumerate(value))
        width = checked_size(width, f"{name}.width")
        height = checked_size(height, f"{name}.height")
        return [round(x, 3), round(y, 3), round(width, 3), round(height, 3)]

    source = signature(record.get("source"), "source")
    target = signature(record.get("target"), "target")
    points = record.get("points")
    if not isinstance(points, (list, tuple)) or not 2 <= len(points) <= MAX_POINTS:
        raise ValueError("Nombre de points de route VSDX invalide")
    normalized = []
    for index, point in enumerate(points):
        if not isinstance(point, (list, tuple)) or len(point) != 2:
            raise ValueError(f"Point de route VSDX invalide : {index}")
        normalized.append([_number(point[0], f"points[{index}].x"),
                           _number(point[1], f"points[{index}].y")])
    for a, b in zip(normalized, normalized[1:]):
        dx, dy = abs(b[0] - a[0]), abs(b[1] - a[1])
        if dx <= EPSILON and dy <= EPSILON:
            raise ValueError("Segment nul dans la route VSDX")
        if dx > EPSILON and dy > EPSILON:
            raise ValueError("Route VSDX diagonale non prise en charge")
    return {"schema": SCHEMA, "source": source, "target": target,
            "points": normalized}


def _crosses_open_rectangle(a, b, bounds):
    left, top, right, bottom = bounds
    x1, y1 = a
    x2, y2 = b
    if abs(x1 - x2) <= EPSILON:
        lo, hi = sorted((y1, y2))
        return left + EPSILON < x1 < right - EPSILON and max(lo, top + EPSILON) < min(hi, bottom - EPSILON)
    if abs(y1 - y2) <= EPSILON:
        lo, hi = sorted((x1, x2))
        return top + EPSILON < y1 < bottom - EPSILON and max(lo, left + EPSILON) < min(hi, right - EPSILON)
    return True


def active_visio_route(edge, source, target, nodes):
    """Return safe imported points, or ``None`` to request normal routing.

    Imported static bends are intentionally invalidated by endpoint resize,
    endpoint movement, malformed metadata or a newly intersected obstacle. The
    ordinary router remains the single safe fallback, with no stale-path reuse.
    """
    record = edge.get("visio_route") if isinstance(edge, dict) else None
    if record is None:
        return None
    if edge.get("routing") != "orthogonal":
        return None
    try:
        route = validate_visio_route(record)
        if route["source"] != node_route_signature(source):
            return None
        if route["target"] != node_route_signature(target):
            return None
        points = [(p[0], p[1]) for p in route["points"]]
        obstacles = []
        for node in nodes:
            if not isinstance(node, dict):
                continue
            # Include endpoint rectangles too: a static path may touch a glue
            # boundary, but must not run through the interior of the device.
            if node.get("shape") == "visio-group":
                continue
            # Corrupt unrelated shapes must not crash rendering; the model
            # validator separately rejects malformed node dimensions.
            try:
                obstacles.append(node_bounds(node))
            except (KeyError, TypeError, ValueError, OverflowError):
                return None
        for a, b in zip(points, points[1:]):
            if any(_crosses_open_rectangle(a, b, rect) for rect in obstacles):
                return None
        return points
    except (KeyError, TypeError, ValueError, OverflowError):
        return None
