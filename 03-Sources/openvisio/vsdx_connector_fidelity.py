"""Independent, strict audit of *public* VSDX connector path geometry.

This checks the static path emitted by OpenVisio, not the embedded JSON and
not Microsoft Visio's dynamic routing or rendering. Coordinates are anchored
against a public top-level node, so moving a whole Visio page does not cause a
false positive. Author: Abdelhalim Talbi.
"""
from math import hypot, isfinite
from xml.etree import ElementTree as ET

from .parallel_geometry import display_edges
from .routing import routing_scene

PX_PER_IN = 96.0
V = 'http://schemas.microsoft.com/office/visio/2011/1/core'


class ConnectorPathFidelityError(ValueError):
    """The public connector geometry differs from the OpenVisio route."""


def _cells(parent):
    result = {}
    for cell in parent.findall(f'{{{V}}}Cell'):
        name = cell.get('N')
        if name in result:
            raise ConnectorPathFidelityError('Cellule VSDX dupliquée : ' + str(name))
        try:
            value = float(cell.get('V'))
        except (ValueError, TypeError) as exc:
            raise ConnectorPathFidelityError('Cellule VSDX non numérique') from exc
        if not isfinite(value):
            raise ConnectorPathFidelityError('Cellule VSDX non finie')
        result[name] = value
    return result


def _public_path(shape):
    """Decode the two static geometry encodings emitted by OpenVisio."""
    cells = _cells(shape)
    try:
        begin = (cells['BeginX'], cells['BeginY'])
        end = (cells['EndX'], cells['EndY'])
    except KeyError as exc:
        raise ConnectorPathFidelityError('Extrémité de connecteur VSDX absente') from exc
    sections = shape.findall(f'{{{V}}}Section')
    geometry = [s for s in sections if s.get('N') == 'Geometry']
    if len(geometry) != 1:
        raise ConnectorPathFidelityError('Section Geometry de connecteur absente ou ambiguë')
    rows = geometry[0].findall(f'{{{V}}}Row')
    kinds = [row.get('T') for row in rows]
    if kinds == ['RelMoveTo', 'RelLineTo']:
        # Historical V42.35 straight links use normalized 0..1 geometry.
        # Accept *only* that canonical form, not arbitrary relative shapes.
        first, last = (_cells(row) for row in rows)
        if any(abs(value) > 1e-9 for value in (first.get('X', float('inf')),
                                                 first.get('Y', float('inf')),
                                                 last.get('X', float('inf')) - 1,
                                                 last.get('Y', float('inf')))):
            raise ConnectorPathFidelityError('Géométrie relative VSDX modifiée')
        return [begin, end]
    if not kinds or kinds[0] != 'MoveTo' or any(kind != 'LineTo' for kind in kinds[1:]):
        raise ConnectorPathFidelityError('Géométrie de connecteur VSDX non prise en charge')
    dx, dy = end[0] - begin[0], end[1] - begin[1]
    length = hypot(dx, dy)
    if length <= 1e-12:
        raise ConnectorPathFidelityError('Connecteur VSDX de longueur nulle')
    ux, uy = dx / length, dy / length
    points = []
    for row in rows:
        row_cells = _cells(row)
        try:
            x, y = row_cells['X'], row_cells['Y']
        except KeyError as exc:
            raise ConnectorPathFidelityError('Coordonnée de connecteur VSDX absente') from exc
        points.append((begin[0] + x * ux - y * uy,
                       begin[1] + x * uy + y * ux))
    return points


def audit_connector_paths(page, document, *, tolerance=0.005):
    """Verify the complete ordered path of each public connector, in pixels.

    A top-level shape's public PinX/PinY is the translation anchor. The audit
    rejects changed elbows, endpoints, order, or missing geometry even when
    node count, connector topology and SAN labels remain unchanged.
    """
    nodes = document['nodes']
    edges = document['edges']
    if not edges:
        return {'connectors_checked': 0, 'route_points_checked': 0}
    top = next((node for node in nodes if not node.get('visio_group_parent')), None)
    if top is None:
        raise ConnectorPathFidelityError('Ancrage de page VSDX absent')
    shapes = page.findall(f'./{{{V}}}Shapes/{{{V}}}Shape')
    anchor = next((s for s in shapes if s.get('ID') == str(nodes.index(top) + 1)), None)
    if anchor is None:
        raise ConnectorPathFidelityError('Forme de référence VSDX absente')
    anchor_cells = _cells(anchor)
    try:
        pin_x, pin_y = anchor_cells['PinX'], anchor_cells['PinY']
    except KeyError as exc:
        raise ConnectorPathFidelityError('Coordonnée de référence VSDX absente') from exc
    connectors = {s.get('ID'): s for s in shapes if s.get('NameU') == 'OpenVisio connector'}
    if len(connectors) != len(edges):
        raise ConnectorPathFidelityError('Nombre de connecteurs publics VSDX incohérent')
    scene = routing_scene(nodes)
    checked = 0
    for index, edge in enumerate(display_edges(edges, nodes), len(nodes) + 1):
        shape = connectors.get(str(index))
        if shape is None:
            raise ConnectorPathFidelityError('Connecteur public VSDX absent : ' + edge['id'])
        actual = _public_path(shape)
        expected_world = scene.route_points(edge)
        expected = [(pin_x + (x - top['x']) / PX_PER_IN,
                     pin_y - (y - top['y']) / PX_PER_IN)
                    for x, y in expected_world]
        if len(actual) != len(expected) or any(
                hypot((ax - ex) * PX_PER_IN, (ay - ey) * PX_PER_IN) > tolerance
                for (ax, ay), (ex, ey) in zip(actual, expected)):
            raise ConnectorPathFidelityError('Tracé public du connecteur VSDX modifié : ' + edge['id'])
        checked += len(expected)
    return {'connectors_checked': len(edges), 'route_points_checked': checked}
