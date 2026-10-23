"""Conservative conversion of unrotated Visio shape pins to center coordinates.

Visio PinX/PinY locate the *local pin*, not necessarily the geometric centre.
A shape with an off-centre LocPinX/LocPinY must be shifted when flattened to
OpenVisio's centre-based nodes. Angle is applied to the centre displacement;
the rotated outline and grouped transforms are not reconstructed.
Author: Abdelhalim Talbi.
"""
import math


def shape_center_inches(cells):
    """Return unrotated shape centre (inches), or raise ValueError for unsafe cells.

    Missing Width/Height keeps legacy PinX/PinY behaviour. When both dimensions
    exist, missing LocPin defaults to the geometric centre, as in a conventional
    Visio rectangle. Rotation shifts the centre but does not preserve orientation.
    """
    try:
        pin_x = float(cells["PinX"])
        pin_y = float(cells["PinY"])
        if not (math.isfinite(pin_x) and math.isfinite(pin_y)):
            raise ValueError("Coordonnée Visio non finie")
        if "Width" not in cells or "Height" not in cells:
            return pin_x, pin_y
        width = float(cells["Width"])
        height = float(cells["Height"])
        if not all(math.isfinite(v) and 0 < v <= 100000 for v in (width, height)):
            raise ValueError("Dimensions Visio invalides")
        loc_x = float(cells.get("LocPinX", width / 2))
        loc_y = float(cells.get("LocPinY", height / 2))
        if not all(math.isfinite(v) for v in (loc_x, loc_y)):
            raise ValueError("Ancrage Visio non fini")
        angle = float(cells.get("Angle", 0))
        if not math.isfinite(angle):
            raise ValueError("Rotation Visio non finie")
        dx, dy = width / 2 - loc_x, height / 2 - loc_y
        center_x = pin_x + dx * math.cos(angle) - dy * math.sin(angle)
        center_y = pin_y + dx * math.sin(angle) + dy * math.cos(angle)
        if not all(math.isfinite(v) and abs(v) <= 1000000 for v in (center_x, center_y)):
            raise ValueError("Centre Visio hors limites")
        return center_x, center_y
    except (KeyError, TypeError, OverflowError) as exc:
        raise ValueError("Géométrie Visio invalide") from exc


def shape_dimensions_inches(cells):
    """Return Visio width/height in inches, defaulting absent dimensions.

    Invalid and unreasonably large rectangles are rejected rather than silently
    creating unusable giant equipment in the OpenVisio editor.
    """
    from .node_geometry import DEFAULT_WIDTH, DEFAULT_HEIGHT, checked_size
    try:
        width = float(cells.get("Width", DEFAULT_WIDTH / 96.0)) * 96.0
        height = float(cells.get("Height", DEFAULT_HEIGHT / 96.0)) * 96.0
        checked_size(width, "width")
        checked_size(height, "height")
        return width / 96.0, height / 96.0
    except (TypeError, ValueError, OverflowError) as exc:
        raise ValueError("Dimensions de forme Visio non représentables") from exc


def shape_axis_aligned_dimensions_inches(cells):
    """Return the exact axis-aligned envelope of a rotated Visio rectangle.

    OpenVisio does not support rotated node outlines. AABB preserves the
    visual footprint for obstacle avoidance, selection and exported geometry.
    It is *not* a lossless Visio rotation import. The centre displacement from
    an off-centre LocPin is handled separately by shape_center_inches().
    """
    from .node_geometry import checked_size
    width, height = shape_dimensions_inches(cells)
    try:
        angle = float(cells.get("Angle", 0))
        if not math.isfinite(angle):
            raise ValueError("Rotation Visio non finie")
        cosine, sine = abs(math.cos(angle)), abs(math.sin(angle))
        envelope_width = width * cosine + height * sine
        envelope_height = width * sine + height * cosine
        # A rotated shape may exceed the editor's maximum dimensions even
        # when its unrotated Width and Height were individually acceptable.
        checked_size(envelope_width * 96.0, "width")
        checked_size(envelope_height * 96.0, "height")
        return envelope_width, envelope_height
    except (TypeError, OverflowError) as exc:
        raise ValueError("Rotation Visio invalide") from exc


def group_local_to_parent_inches(cells, x, y):
    """Map a point from a Visio group's local coordinates to its parent.

    Visio's child Pin coordinates are relative to the group's lower-left
    origin. LocPin is the pivot, not necessarily the centre of the group.
    Reject incomplete geometry instead of guessing a child position.
    """
    try:
        width = float(cells['Width'])
        height = float(cells['Height'])
        pin_x, pin_y = float(cells['PinX']), float(cells['PinY'])
        angle = float(cells.get('Angle', 0))
        loc_x = float(cells.get('LocPinX', width / 2))
        loc_y = float(cells.get('LocPinY', height / 2))
        values = (width, height, pin_x, pin_y, angle, loc_x, loc_y, x, y)
        if not all(math.isfinite(v) for v in values) or not (0 < width <= 100000 and 0 < height <= 100000):
            raise ValueError('Transformation de groupe Visio non finie')
        dx, dy = x - loc_x, y - loc_y
        out_x = pin_x + dx * math.cos(angle) - dy * math.sin(angle)
        out_y = pin_y + dx * math.sin(angle) + dy * math.cos(angle)
        if not all(math.isfinite(v) and abs(v) <= 1000000 for v in (out_x, out_y)):
            raise ValueError('Transformation de groupe Visio hors limites')
        return out_x, out_y
    except (KeyError, TypeError, OverflowError, ValueError) as exc:
        raise ValueError('Transformation de groupe Visio invalide') from exc


def nested_shape_geometry_inches(cells, ancestors):
    """Return centre and AABB dimensions after all ancestor transforms.

    Ancestors are ordered outermost to innermost. Only the bounding rectangle
    is preserved; rotation, group semantics and master geometry remain lossy.
    """
    x, y = shape_center_inches(cells)
    for parent in reversed(ancestors):
        x, y = group_local_to_parent_inches(parent, x, y)
    width, height = shape_dimensions_inches(cells)
    try:
        angle = float(cells.get('Angle', 0)) + sum(float(p.get('Angle', 0)) for p in ancestors)
        if not math.isfinite(angle):
            raise ValueError('Rotation Visio non finie')
        c, s = abs(math.cos(angle)), abs(math.sin(angle))
        from .node_geometry import checked_size
        bw, bh = width * c + height * s, width * s + height * c
        checked_size(bw * 96.0, 'width')
        checked_size(bh * 96.0, 'height')
        return x, y, bw, bh, angle
    except (TypeError, OverflowError) as exc:
        raise ValueError('Géométrie Visio groupée invalide') from exc
