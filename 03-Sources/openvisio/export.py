"""Native Python SVG export with safe viewBox and shared connector labels.

Author: Abdelhalim Talbi.
"""
from pathlib import Path
from math import isfinite
from xml.sax.saxutils import escape, quoteattr

from .model import validate
from .layers import project_visible
from .shapes import get_shape
from .routing import routing_scene
from .node_geometry import node_bounds, node_dimensions
from .parallel_geometry import display_edges
from .connector_labels import layout_connector_labels
from .shape_icons import equipment_icon


def _xml10_text(value):
    """Replace XML 1.0 forbidden code points without mutating source captions.

    Imported Visio/VSDX text can contain control characters or unpaired
    surrogates. XML escaping alone does not make those characters legal SVG.
    """
    return ''.join(
        char if (char in "\t\n\r" or 0x20 <= ord(char) <= 0xD7FF
                 or 0xE000 <= ord(char) <= 0xFFFD
                 or 0x10000 <= ord(char) <= 0x10FFFF)
        else "\ufffd"
        for char in str(value)
    )


def to_svg(data, width=None, height=None, margin=80, *, include_hidden_layers=False):
    """Export the diagram as displayed in the editor by default.

    Hidden layers and edges attached to hidden equipment must not leak into
    the visual export. The opt-in full export preserves the previous behavior.
    This projection does not alter the persisted document or undo history.
    """
    if (isinstance(margin, bool) or not isinstance(margin, (int, float))
            or not isfinite(margin) or margin < 0):
        raise ValueError("Marge SVG invalide")
    data = validate(data)
    if not include_hidden_layers:
        data = project_visible(data)
    nodes = {n['id']: n for n in data['nodes']}
    scene = routing_scene(data['nodes'])
    routed = [(edge, scene.route_points(edge))
              for edge in display_edges(data['edges'], data['nodes'])]
    label_layout = layout_connector_labels(data['nodes'], data['edges'], scene=scene)

    if nodes:
        bounds = [node_bounds(n) for n in nodes.values()]
        # Do not clip detours outside the equipment envelope, or labels which
        # have been moved outside the dense SAN topology to avoid collisions.
        for _, points in routed:
            bounds.extend((x, y, x, y) for x, y in points)
        bounds.extend(label.bounds for label in label_layout.labels.values())
        min_x = min(b[0] for b in bounds) - margin
        max_x = max(b[2] for b in bounds) + margin
        min_y = min(b[1] for b in bounds) - margin
        max_y = max(b[3] for b in bounds) + margin
    else:
        min_x, min_y, max_x, max_y = 0, 0, 800, 600
    natural_width, natural_height = max_x - min_x, max_y - min_y
    width = natural_width if width is None else width
    height = natural_height if height is None else height
    if (any(isinstance(value, bool) or not isinstance(value, (int, float))
            or not isfinite(value) or value <= 0
            for value in (width, height, natural_width, natural_height))):
        raise ValueError('Dimensions SVG invalides')
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {natural_width} {natural_height}">',
             f'<rect x="{min_x}" y="{min_y}" width="{natural_width}" height="{natural_height}" fill="#f8fafc"/>']
    if routed:
        # Tk draws arrow=tk.LAST for every connector. SVG previously omitted
        # direction entirely: bidirectional FC paths were indistinguishable
        # outside the editor. A single reusable marker preserves the final
        # segment direction for straight and orthogonal routes alike.
        lines.append('<defs><marker id="openvisio-san-arrow" markerWidth="10" '
                     'markerHeight="8" refX="9" refY="4" orient="auto" '
                     'markerUnits="userSpaceOnUse">'
                     '<path d="M 0 0 L 10 4 L 0 8 z" fill="#2563eb"/>'
                     '</marker></defs>')
    for edge, points in routed:
        # Separate path identity from caption metadata: blank connector
        # labels must remain blank, while each parallel FC path is traceable.
        connector_id = quoteattr(_xml10_text(edge['id']))
        if len(points) == 2:
            (ax, ay), (bx, by) = points
            lines.append(f'<line data-openvisio-connector={connector_id} '
                         f'x1="{ax:g}" y1="{ay:g}" x2="{bx:g}" y2="{by:g}" '
                         'stroke="#2563eb" stroke-width="2" '
                         'marker-end="url(#openvisio-san-arrow)"/>')
        else:
            poly = ' '.join(f'{x},{y}' for x, y in points)
            lines.append(f'<polyline data-openvisio-connector={connector_id} '
                         f'points="{poly}" fill="none" stroke="#2563eb" '
                         'stroke-width="2" marker-end="url(#openvisio-san-arrow)"/>')
    for label in label_layout.labels.values():
        lines.append(f'<text data-openvisio-edge={quoteattr(_xml10_text(label.edge_id))} '
                     f'x="{label.x:g}" y="{label.y:g}" text-anchor="middle" '
                     f'font-family="Arial" font-size="9" fill="#334155" '
                     f'dominant-baseline="central">{escape(_xml10_text(label.text))}</text>')
    if label_layout.hidden:
        hidden = ', '.join(label_layout.hidden)
        lines.append(f'<desc>Connector labels omitted for insufficient space: {escape(_xml10_text(hidden))}</desc>')
    for node in data['nodes']:
        x, y = node['x'], node['y']
        label = escape(_xml10_text(node.get('label', 'Équipement')))
        fill = get_shape(node.get('shape', 'server'))['fill']
        w, h = node_dimensions(node)
        lines.append(f'<rect x="{x-w/2:g}" y="{y-h/2:g}" width="{w:g}" height="{h:g}" rx="8" fill="{fill}" stroke="#1d4ed8"/>')
        icon = equipment_icon(node)
        if icon is not None:
            points = ' '.join(f'{px:g},{py:g}' for px, py in icon)
            lines.append(f'<polygon data-openvisio-node-icon={quoteattr(_xml10_text(node["id"]))} '
                         f'points="{points}" fill="#f8fafc" stroke="#334155"/>')
        lines.append(f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="13" fill="#172554">{label}</text>')
    lines.append('</svg>')
    return '\n'.join(lines)


def export_svg(path, data, *, include_hidden_layers=False,
               expected_sha256=None, require_absent=False, lock_timeout=5.0):
    """Atomically export SVG with optional optimistic/no-clobber guards.

    Rendering completes before taking the destination lock. A failed SVG
    rendering never truncates an existing diagram. The lock serializes
    cooperating OpenVisio writers; external writers ignoring it are not
    guaranteed to be serialized. Return SHA-256 of the published bytes.
    """
    import hashlib
    import os
    import tempfile
    from .model import SaveConflict, _sha256
    from .save_lock import exclusive_document_lock

    if require_absent and expected_sha256 is not None:
        raise ValueError("Préconditions SVG incompatibles")
    if expected_sha256 is not None and (
            not isinstance(expected_sha256, str) or len(expected_sha256) != 64
            or any(ch not in "0123456789abcdef" for ch in expected_sha256)):
        raise ValueError("Empreinte SVG invalide")
    payload = to_svg(data, include_hidden_layers=include_hidden_layers).encode("utf-8")
    revision = hashlib.sha256(payload).hexdigest()
    destination = Path(path)

    def check_revision():
        if require_absent:
            if destination.exists() or destination.is_symlink():
                raise SaveConflict("Le SVG de destination existe déjà")
        elif expected_sha256 is not None:
            try:
                current = _sha256(destination)
            except FileNotFoundError as exc:
                raise SaveConflict("Le SVG a disparu depuis son ouverture") from exc
            if current != expected_sha256:
                raise SaveConflict("Le SVG a changé depuis son ouverture")

    try:
        with exclusive_document_lock(destination, timeout=lock_timeout):
            check_revision()
            destination.parent.mkdir(parents=True, exist_ok=True)
            fd, temporary = tempfile.mkstemp(
                prefix=".openvisio-svg-", suffix=".tmp", dir=destination.parent)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(payload)
                    stream.flush()
                    os.fsync(stream.fileno())
                check_revision()
                if require_absent:
                    try:
                        os.link(temporary, destination)
                    except FileExistsError as exc:
                        raise SaveConflict("Le SVG a été créé pendant l'export") from exc
                else:
                    os.replace(temporary, destination)
                return revision
            finally:
                if os.path.exists(temporary):
                    os.unlink(temporary)
    except TimeoutError as exc:
        raise SaveConflict(str(exc)) from exc
