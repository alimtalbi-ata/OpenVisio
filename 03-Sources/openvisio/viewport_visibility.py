"""Exact, conservative visibility predicates for the editor canvas.

Only screen painting is culled. Routing, hit-testing, serialization and export
continue to use the complete document. In particular an orthogonal connector
may enter the viewport even when both endpoint nodes are outside it.
Author: Abdelhalim Talbi.
"""
from math import isfinite


def view_window(viewport, width, height, margin_px=24):
    """World-space screen rectangle, expanded by a fixed pixel margin.

    The caller must provide a positive viewport zoom. A small or not-yet-sized
    Tk canvas is valid; the returned rectangle still contains its origin.
    """
    if margin_px < 0 or not isfinite(margin_px):
        raise ValueError('Invalid canvas visibility margin')
    if width < 0 or height < 0:
        raise ValueError('Invalid canvas dimensions')
    if not isfinite(viewport.zoom) or viewport.zoom <= 0:
        raise ValueError('Invalid viewport zoom')
    x0, y0 = viewport.world(-margin_px, -margin_px)
    x1, y1 = viewport.world(width + margin_px, height + margin_px)
    return min(x0, x1), min(y0, y1), max(x0, x1), max(y0, y1)


def rect_visible(rect, window):
    """Inclusive AABB overlap; false positives are safe, false negatives aren't."""
    return (rect[0] <= window[2] and rect[2] >= window[0]
            and rect[1] <= window[3] and rect[3] >= window[1])


def polyline_visible(points, window):
    """Conservative path visibility, including paths crossing with endpoints offscreen.

    The segment AABB check can overestimate visibility for diagonal lines, but
    it never excludes a visible segment. Routing paths are not simplified here.
    """
    if not points:
        return False
    if len(points) == 1:
        x, y = points[0]
        return rect_visible((x, y, x, y), window)
    for (ax, ay), (bx, by) in zip(points, points[1:]):
        if rect_visible((min(ax, bx), min(ay, by),
                         max(ax, bx), max(ay, by)), window):
            return True
    return False
