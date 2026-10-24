"""Pure world/screen coordinate transforms for diagram navigation. Author: Abdelhalim Talbi."""
import math
from .node_geometry import node_bounds

MIN_ZOOM = 0.001  # Fit and interactive wheel/menu zoom share one minimum.
MAX_ZOOM = 4.0

class Viewport:
    def __init__(self, zoom=1.0, offset_x=0.0, offset_y=0.0):
        # Invalid persisted view state must not propagate into Tk coordinates.
        values = (zoom, offset_x, offset_y)
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for v in values) or zoom <= 0:
            raise ValueError("Viewport zoom must be positive; offsets must be finite")
        self.zoom = float(zoom)
        self.offset_x = float(offset_x)
        self.offset_y = float(offset_y)

    @staticmethod
    def _finite_point(x, y):
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for v in (x, y)):
            raise ValueError("Viewport coordinates must be finite numbers")

    def screen(self, x, y):
        self._finite_point(x, y)
        sx, sy = x * self.zoom + self.offset_x, y * self.zoom + self.offset_y
        self._finite_point(sx, sy)
        return sx, sy

    def world(self, x, y):
        self._finite_point(x, y)
        wx, wy = (x - self.offset_x) / self.zoom, (y - self.offset_y) / self.zoom
        self._finite_point(wx, wy)
        return wx, wy

    def zoom_at(self, factor, x, y):
        """Zoom around the pointer without corrupting state on invalid input."""
        values = (factor, x, y, self.zoom, self.offset_x, self.offset_y)
        if not all(isinstance(v, (int, float)) and math.isfinite(v) for v in values):
            raise ValueError("Zoom and pointer coordinates must be finite numbers")
        if factor <= 0 or self.zoom <= 0:
            raise ValueError("Zoom factor and current zoom must be positive")
        wx, wy = self.world(x, y)
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, self.zoom * factor))
        new_x = x - wx * new_zoom
        new_y = y - wy * new_zoom
        if not all(math.isfinite(v) for v in (new_zoom, new_x, new_y)):
            raise ValueError("Zoom would produce non-finite coordinates")
        self.zoom, self.offset_x, self.offset_y = new_zoom, new_x, new_y

    def pan(self, dx, dy):
        if not all(isinstance(v, (int, float)) and math.isfinite(v)
                   for v in (dx, dy, self.offset_x, self.offset_y)):
            raise ValueError("Pan offsets must be finite numbers")
        new_x, new_y = self.offset_x + dx, self.offset_y + dy
        if not math.isfinite(new_x) or not math.isfinite(new_y):
            raise ValueError("Pan would produce non-finite coordinates")
        self.offset_x, self.offset_y = new_x, new_y

    def _fit_boxes(self, bounds, screen_width, screen_height, margin):
        """Commit a view only after validating the complete visible extent."""
        dimensions = (screen_width, screen_height, margin)
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for v in dimensions):
            raise ValueError("Canvas dimensions and margin must be finite numbers")
        if screen_width <= 0 or screen_height <= 0 or margin < 0:
            raise ValueError("Canvas dimensions must be positive and margin nonnegative")
        if not bounds:
            self.zoom, self.offset_x, self.offset_y = 1.0, 0.0, 0.0
            return
        if not all(isinstance(v, (int, float)) and not isinstance(v, bool)
                   and math.isfinite(v) for box in bounds for v in box):
            raise ValueError("Diagram bounds must be finite numbers")
        left = min(b[0] for b in bounds)
        right = max(b[2] for b in bounds)
        top = min(b[1] for b in bounds)
        bottom = max(b[3] for b in bounds)
        span_x, span_y = right - left, bottom - top
        if not math.isfinite(span_x) or not math.isfinite(span_y):
            raise ValueError("Diagram span is too large to fit safely")
        usable_width = max(1, screen_width - 2 * margin)
        usable_height = max(1, screen_height - 2 * margin)
        new_zoom = max(MIN_ZOOM, min(MAX_ZOOM, min(
            usable_width / max(1, span_x),
            usable_height / max(1, span_y))))
        new_x = screen_width / 2 - (left + right) / 2 * new_zoom
        new_y = screen_height / 2 - (top + bottom) / 2 * new_zoom
        if not all(math.isfinite(v) for v in (new_zoom, new_x, new_y)):
            raise ValueError("Fit would produce non-finite coordinates")
        self.zoom, self.offset_x, self.offset_y = new_zoom, new_x, new_y

    def fit(self, nodes, screen_width, screen_height, margin=80):
        """Fit node bounds, preserving the viewport on invalid geometry."""
        self._fit_boxes([node_bounds(node) for node in nodes],
                        screen_width, screen_height, margin)

    def fit_scene(self, nodes, edges, screen_width, screen_height, margin=80):
        """Fit nodes, routed SAN paths and *visible* connector captions.

        This is a derived view: physical FC port/fabric data and document
        coordinates are never modified. A failed route leaves the old view
        intact rather than displaying an incomplete fabric.
        """
        from .routing import routing_scene
        from .parallel_geometry import display_edges
        from .connector_labels import layout_connector_labels

        boxes = [node_bounds(node) for node in nodes]
        if edges:
            scene = routing_scene(nodes)
            for edge in display_edges(edges, nodes):
                boxes.extend((x, y, x, y) for x, y in scene.route_points(edge))
            labels = layout_connector_labels(nodes, edges, scene=scene)
            boxes.extend(label.bounds for label in labels.labels.values())
        self._fit_boxes(boxes, screen_width, screen_height, margin)
