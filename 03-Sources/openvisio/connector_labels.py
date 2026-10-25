"""Deterministic, collision-aware labels for SAN connectors.

Pure world-space layout shared by the Tk canvas and SVG renderer.  The
placement is a derived view: it never changes diagram persistence, routing,
or the physical identity of a SAN path.

Author: Abdelhalim Talbi.
"""
from dataclasses import dataclass
from math import floor, hypot

from .node_geometry import node_bounds
from .parallel_geometry import display_edges
from .routing import RoutingError, routing_scene


@dataclass(frozen=True)
class ConnectorLabel:
    edge_id: str
    text: str
    x: float
    y: float
    bounds: tuple


@dataclass(frozen=True)
class LabelLayout:
    labels: dict
    hidden: tuple


def _metadata_text(value):
    """Render optional imported metadata without inventing a literal 'None'."""
    return '' if value is None else str(value).strip()


def edge_label_text(edge):
    """Return the same bounded, human-readable text on every output surface."""
    # Visio connector captions are free-form text. Do not reinterpret them
    # as SAN metadata or replace them with a generated protocol/port summary.
    # A whitespace-only caption is not an intentional override: keep the
    # physical FC fabric/port metadata visible in Tk, SVG and public VSDX.
    explicit = _metadata_text(edge.get("label"))
    if explicit:
        return explicit[:72]
    parts = []
    for key in ('protocol',):
        value = _metadata_text(edge.get(key))
        if value:
            parts.append(value)
    speed = _metadata_text(edge.get('speed_gbps'))
    if speed:
        parts.append(speed + ' Gbit/s')
    fabric = _metadata_text(edge.get('fabric'))
    if fabric:
        parts.append('Fabric ' + fabric)
    ports = ' → '.join(_metadata_text(edge.get(key))
                       for key in ('source_port', 'target_port')
                       if _metadata_text(edge.get(key)))
    if ports:
        parts.append(ports)
    return ' · '.join(parts)[:72]


class _SpatialBoxes:
    """Bounded spatial hash: huge coordinates cannot explode the cell index."""
    def __init__(self, cell=128):
        self.cell = cell
        self.grid = {}
        self.large = []
        self.boxes = []

    def _cells(self, bounds):
        x0, y0, x1, y1 = bounds
        left, right = floor(x0 / self.cell), floor(x1 / self.cell)
        top, bottom = floor(y0 / self.cell), floor(y1 / self.cell)
        if (right - left + 1) * (bottom - top + 1) > 64:
            return None
        return ((x, y) for x in range(left, right + 1)
                for y in range(top, bottom + 1))

    def add(self, bounds):
        index = len(self.boxes)
        self.boxes.append(bounds)
        cells = self._cells(bounds)
        if cells is None:
            self.large.append(index)
        else:
            for cell in cells:
                self.grid.setdefault(cell, []).append(index)

    def intersects(self, bounds, gap=0):
        x0, y0, x1, y1 = bounds
        expanded = (x0-gap, y0-gap, x1+gap, y1+gap)
        cells = self._cells(expanded)
        candidates = set(self.large)
        if cells is None:
            candidates.update(range(len(self.boxes)))
        else:
            for cell in cells:
                candidates.update(self.grid.get(cell, ()))
        for i in candidates:
            a, b, c, d = self.boxes[i]
            if expanded[0] < c and expanded[2] > a and expanded[1] < d and expanded[3] > b:
                return True
        return False


def layout_connector_labels(nodes, edges, scene=None):
    """Place connector metadata without colliding with equipment or other labels.

    The returned coordinates are in document units and do not depend on zoom,
    viewport position, input edge ordering, or the Tk runtime.  If a safe
    position cannot be found, the edge ID is returned in hidden instead
    of silently drawing illegible overlapping text.
    """
    scene = scene if scene is not None else routing_scene(nodes)
    occupied = _SpatialBoxes()
    for node in nodes:
        # Visio group outlines are transparent containers, not obstacles.
        if node.get('shape') != 'visio-group':
            occupied.add(node_bounds(node))

    # Resolve the geometry first so that labels cannot obscure another SAN
    # path.  Indexing the bounding boxes of individual segments is safe for
    # horizontal/vertical routes and conservatively avoids diagonal routes.
    segments = _SpatialBoxes()
    visible = []
    decorated = display_edges(edges, nodes)
    # When no connector has a label, avoid routing any edge at all. Otherwise
    # every connector is an obstacle, including those without metadata. The
    # previous implementation omitted unlabelled paths from the segment index,
    # allowing SAN labels to cover otherwise visible unlabelled links.
    if not any(edge_label_text(edge) for edge in decorated):
        return LabelLayout({}, ())
    for edge in decorated:
        text = edge_label_text(edge)
        try:
            points = scene.route_points(edge)
        except RoutingError:
            # An unroutable edge cannot provide reliable obstacle geometry.
            continue
        for a, b in zip(points, points[1:]):
            if a == b:
                continue
            segments.add((min(a[0], b[0])-2, min(a[1], b[1])-2,
                          max(a[0], b[0])+2, max(a[1], b[1])+2))
        if text:
            visible.append((edge, points, text))

    # Stable across edge reorder, and independent of unrelated document edits.
    visible.sort(key=lambda item: str(item[0]['id']))
    labels, hidden = {}, []
    for edge, points, text in visible:
        # Tk draws explicit newlines on separate rows. Use the longest line
        # for horizontal clearance and reserve one line-height per row so the
        # collision index protects the full visible caption in both Tk and SVG.
        text_lines = text.replace("\r\n", "\n").replace("\r", "\n").split("\n")
        width = max(24.0, max(len(line) for line in text_lines) * 5.2 + 10.0)
        height = 15.0 * len(text_lines)
        ranked = sorted(enumerate(zip(points, points[1:])),
                        key=lambda entry: (-hypot(entry[1][1][0]-entry[1][0][0],
                                                   entry[1][1][1]-entry[1][0][1]), entry[0]))
        placed = None
        for _, (start, end) in ranked[:8]:
            dx, dy = end[0]-start[0], end[1]-start[1]
            length = hypot(dx, dy)
            if length < 1:
                continue
            nx, ny = -dy/length, dx/length
            for fraction in (0.5, 0.25, 0.75, 0.1, 0.9):
                mid_x, mid_y = start[0]+fraction*dx, start[1]+fraction*dy
                for step in range(10):
                    for sign in (-1, 1):
                        offset = sign*(15.0 + step*16.0)
                        x, y = mid_x+nx*offset, mid_y+ny*offset
                        box = (x-width/2, y-height/2, x+width/2, y+height/2)
                        if (occupied.intersects(box, gap=3)
                                or segments.intersects(box, gap=2)):
                            continue
                        placed = ConnectorLabel(edge['id'], text, x, y, box)
                        break
                    if placed:
                        break
                if placed:
                    break
            if placed:
                break
        if placed is None:
            hidden.append(edge['id'])
        else:
            labels[edge['id']] = placed
            occupied.add(placed.bounds)
    return LabelLayout(labels, tuple(hidden))
