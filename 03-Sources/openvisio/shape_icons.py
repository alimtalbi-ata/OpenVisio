"""Small, topology-aware equipment pictograms shared by Tk and SVG.

These are deliberately stylized, not licensed vendor or Visio stencils.
Author: Abdelhalim Talbi.
"""

from .node_geometry import node_dimensions

# Closed normalized silhouettes: visually distinct even at modest zoom.
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


def equipment_icon(node):
    """Return world-space polygon for an explicit equipment type, or None.

    Avoid crowding tiny equipment and transparent Visio group containers.
    Never mutate the diagram; zoom is applied by each renderer afterwards.
    """
    kind = node.get("shape")
    if kind not in _ICONS:
        return None
    width, height = node_dimensions(node)
    if width < 80 or height < 40:
        return None
    size = min(20.0, height * .35, width * .15)
    left = node["x"] - width / 2 + 8
    top = node["y"] - height / 2 + 8
    return tuple((left + px * size, top + py * size)
                 for px, py in _ICONS[kind])
