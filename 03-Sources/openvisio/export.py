"""Native Python SVG export with safe viewBox and shared connector labels.

Author: Abdelhalim Talbi.
"""
from pathlib import Path
from xml.sax.saxutils import escape, quoteattr

from .model import validate
from .shapes import get_shape
from .routing import routing_scene
from .node_geometry import node_bounds, node_dimensions
from .parallel_geometry import display_edges
from .connector_labels import layout_connector_labels


def to_svg(data, width=None, height=None, margin=80):
    data = validate(data)
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
    if (not isinstance(width, (int, float)) or not isinstance(height, (int, float))
            or width <= 0 or height <= 0):
        raise ValueError('Dimensions SVG invalides')
    lines = [f'<svg xmlns="http://www.w3.org/2000/svg" width="{width}" height="{height}" viewBox="{min_x} {min_y} {natural_width} {natural_height}">',
             f'<rect x="{min_x}" y="{min_y}" width="{natural_width}" height="{natural_height}" fill="#f8fafc"/>']
    for edge, points in routed:
        if len(points) == 2:
            (ax, ay), (bx, by) = points
            lines.append(f'<line x1="{ax:g}" y1="{ay:g}" x2="{bx:g}" y2="{by:g}" stroke="#2563eb" stroke-width="2"/>')
        else:
            poly = ' '.join(f'{x},{y}' for x, y in points)
            lines.append(f'<polyline points="{poly}" fill="none" stroke="#2563eb" stroke-width="2"/>')
    for label in label_layout.labels.values():
        lines.append(f'<text data-openvisio-edge={quoteattr(label.edge_id)} '
                     f'x="{label.x:g}" y="{label.y:g}" text-anchor="middle" '
                     f'font-family="Arial" font-size="9" fill="#334155" '
                     f'dominant-baseline="central">{escape(label.text)}</text>')
    if label_layout.hidden:
        hidden = ', '.join(label_layout.hidden)
        lines.append(f'<desc>Connector labels omitted for insufficient space: {escape(hidden)}</desc>')
    for node in data['nodes']:
        x, y = node['x'], node['y']
        label = escape(str(node.get('label', 'Équipement')))
        fill = get_shape(node.get('shape', 'server'))['fill']
        w, h = node_dimensions(node)
        lines.extend([f'<rect x="{x-w/2:g}" y="{y-h/2:g}" width="{w:g}" height="{h:g}" rx="8" fill="{fill}" stroke="#1d4ed8"/>',
                      f'<text x="{x}" y="{y+5}" text-anchor="middle" font-family="Arial" font-size="13" fill="#172554">{label}</text>'])
    lines.append('</svg>')
    return '\n'.join(lines)


def export_svg(path, data):
    Path(path).write_text(to_svg(data), encoding='utf-8')
