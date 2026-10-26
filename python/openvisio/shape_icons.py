"""Distinct infrastructure outlines and detailed equipment pictograms.

The glyphs are original, schematic symbols shared by Tk and SVG. They are not
licensed vendor or Microsoft Visio stencils. Author: Abdelhalim Talbi.
"""
from math import pi, sin

from .node_geometry import node_dimensions

# Normalized small badges. Their left-hand placement leaves a stable text area.
_ICONS = {
    "server": ((0, 0), (1, 0), (1, 1), (0, 1)),
    "storage": ((.16, 0), (.84, 0), (1, .25), (1, .75), (.84, 1), (.16, 1), (0, .75), (0, .25)),
    "san-switch": ((.12, 0), (.88, 0), (1, 1), (0, 1)),
    "switch": ((.25, 0), (.75, 0), (1, .25), (1, .75), (.75, 1), (.25, 1), (0, .75), (0, .25)),
    "network-switch": ((.5, 0), (1, .5), (.5, 1), (0, .5)),
    "nas": ((.25, 0), (.75, 0), (1, .25), (1, 1), (0, 1), (0, .25)),
    "firewall": ((.5, 0), (1, .2), (.9, .75), (.5, 1), (.1, .75), (0, .2)),
    "database": ((.25, 0), (.75, 0), (1, .25), (1, .8), (.75, 1), (.25, 1), (0, .8), (0, .25)),
    "application": ((.25, 0), (.75, 0), (1, .5), (.75, 1), (.25, 1), (0, .5)),
}

# Full-node silhouettes. Coordinates are normalized to each node's box.
_OUTLINES = {
    "server": ((0, 0), (1, 0), (1, 1), (0, 1)),
    "storage": ((.12, 0), (.88, 0), (1, .18), (1, .82), (.88, 1), (.12, 1), (0, .82), (0, .18)),
    "san-switch": ((.08, 0), (.92, 0), (1, .22), (.96, 1), (.04, 1), (0, .22)),
    "switch": ((.16, 0), (.84, 0), (1, .22), (1, .78), (.84, 1), (.16, 1), (0, .78), (0, .22)),
    "network-switch": ((.5, 0), (1, .5), (.5, 1), (0, .5)),
    "nas": ((.22, 0), (.78, 0), (1, .22), (1, 1), (0, 1), (0, .22)),
    "firewall": ((.5, 0), (1, .18), (.92, .72), (.5, 1), (.08, .72), (0, .18)),
    # database is generated as a faceted cylinder, with elliptical rims.
    "database": None,
    "application": ((.22, 0), (.78, 0), (1, .5), (.78, 1), (.22, 1), (0, .5)),
}


def _icon_box(node):
    kind = node.get("shape")
    if kind not in _ICONS:
        return None
    width, height = node_dimensions(node)
    if width < 80 or height < 40:
        return None
    size = min(24.0, height * .40, width * .20)
    left = node["x"] - width / 2 + 8
    top = node["y"] - height / 2 + 8
    return left, top, size


def equipment_icon(node):
    """Return the badge silhouette polygon, or None for small/unknown nodes."""
    box = _icon_box(node)
    if box is None:
        return None
    left, top, size = box
    return tuple((left + px * size, top + py * size)
                 for px, py in _ICONS[node["shape"]])


def equipment_outline(node):
    """Return an original shape-specific body outline in world coordinates.

    The diagram keeps rectangular bounds for hit testing and connector anchors;
    only its visual body changes. Unsupported/legacy types use the old rectangle.
    """
    kind = node.get("shape")
    width, height = node_dimensions(node)
    if kind not in _OUTLINES or width < 80 or height < 40:
        return None
    left, top = node["x"] - width / 2, node["y"] - height / 2
    if kind == "database":
        points = []
        # Closed faceted cylinder: top and bottom rims remain visible at low zoom.
        for index in range(9):
            t = index / 8
            points.append((t, .18 - .12 * sin(t * pi)))
        points.append((1, .82))
        for index in range(8, -1, -1):
            t = index / 8
            points.append((t, .82 + .12 * sin(t * pi)))
    else:
        points = _OUTLINES[kind]
    return tuple((left + px * width, top + py * height) for px, py in points)


def equipment_detail_primitives(node):
    """Return stable line/polygon details for an equipment badge.

    Each item is {"kind": "line"|"polygon", "points": (...), ...} and is
    directly consumable by both the retained Tk renderer and SVG exporter.
    """
    box = _icon_box(node)
    if box is None:
        return ()
    left, top, size = box
    kind = node["shape"]

    def point(x, y):
        return (left + x * size, top + y * size)

    result = []

    def line(*points, width=1.15):
        result.append({"kind": "line", "points": tuple(point(x, y) for x, y in points),
                       "stroke": "#334155", "width": width})

    def polygon(points, *, fill="#f8fafc", width=1.0):
        result.append({"kind": "polygon", "points": tuple(point(x, y) for x, y in points),
                       "fill": fill, "stroke": "#334155", "width": width})

    def led(x, y, radius=.035):
        polygon(((x-radius, y-radius), (x+radius, y-radius),
                 (x+radius, y+radius), (x-radius, y+radius)), fill="#16a34a", width=.55)

    if kind == "server":
        line((.16, .34), (.84, .34)); line((.16, .62), (.84, .62))
        led(.24, .18); led(.24, .47); led(.24, .76)
        line((.38, .18), (.78, .18), width=.8)
        line((.38, .47), (.78, .47), width=.8)
        line((.38, .76), (.78, .76), width=.8)
    elif kind == "storage":
        line((.34, .12), (.34, .88)); line((.66, .12), (.66, .88))
        line((.20, .30), (.80, .30)); line((.20, .55), (.80, .55)); line((.20, .78), (.80, .78))
        led(.25, .20); led(.75, .68)
    elif kind == "san-switch":
        line((.16, .30), (.84, .30)); line((.14, .53), (.86, .53)); line((.14, .78), (.86, .78))
        for x in (.24, .38, .52, .66, .80):
            line((x, .55), (x, .75), width=.85)
        led(.23, .17); led(.34, .17); led(.45, .17)
    elif kind == "switch":
        line((.50, .18), (.50, .82)); line((.18, .50), (.82, .50))
        for x, y in ((.28, .28), (.72, .28), (.28, .72), (.72, .72)):
            polygon(((x-.07, y-.07), (x+.07, y-.07), (x+.07, y+.07), (x-.07, y+.07)), width=.8)
    elif kind == "network-switch":
        line((.24, .50), (.50, .26), (.76, .50), (.50, .74), (.24, .50))
        line((.50, .26), (.50, .74)); line((.24, .50), (.76, .50))
        led(.50, .50)
    elif kind == "nas":
        line((.22, .40), (.78, .40)); line((.22, .70), (.78, .70))
        led(.32, .24); led(.32, .55)
        line((.48, .24), (.74, .24), width=.8)
    elif kind == "firewall":
        line((.16, .34), (.84, .34)); line((.12, .63), (.88, .63))
        line((.34, .18), (.34, .34)); line((.67, .34), (.67, .63))
        line((.23, .63), (.23, .81)); line((.76, .63), (.76, .78))
    elif kind == "database":
        top_rim = tuple((.16 + .68*i/8, .25 - .10*sin(pi*i/8)) for i in range(9))
        bottom_rim = tuple((.16 + .68*i/8, .72 + .10*sin(pi*i/8)) for i in range(9))
        line(*top_rim); line((.16, .25), (.16, .72)); line((.84, .25), (.84, .72)); line(*bottom_rim)
    elif kind == "application":
        polygon(((.19, .18), (.81, .18), (.81, .63), (.19, .63)), fill="", width=1.0)
        line((.50, .63), (.50, .78)); line((.33, .82), (.67, .82))
        line((.28, .30), (.72, .30), width=.8)
        line((.28, .42), (.60, .42), width=.8)
    return tuple(result)
