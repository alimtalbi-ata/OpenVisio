"""Independent public-page VSDX fidelity gate (not a Microsoft Visio certification).

Verifies that the public XML geometry, group hierarchy, and connector topology
survive import *without* the private OpenVisio document.json payload.
Author: Abdelhalim Talbi.
"""
from pathlib import Path
from collections import Counter
from zipfile import ZipFile
from .model import validate


class PublicVsdxFidelityError(ValueError):
    """Public VSDX pages cannot reproduce the supported document topology."""


def audit_public_vsdx(archive_path, document, *, tolerance=0.005):
    """Compare supported public-page properties against a validated source.

    Node IDs and the absolute page origin are intentionally not compared:
    the external VSDX importer generates sheet IDs and normalizes the origin.
    Edge routing style, masters, rotations, formulas and Visio rendering are
    outside this audit's contract and must be qualified separately.
    """
    from .vsdx_external import import_external_pages
    doc = validate(document)
    try:
        with ZipFile(archive_path) as archive:
            public = import_external_pages(archive)
    except (KeyError, ValueError, OSError, RuntimeError) as exc:
        raise PublicVsdxFidelityError('Pages VSDX publiques illisibles') from exc

    nodes = doc['nodes']
    actual = public['nodes']
    edges = doc['edges']
    links = public['edges']
    if len(nodes) != len(actual) or len(edges) != len(links):
        raise PublicVsdxFidelityError('Nombre de formes ou connecteurs modifié')
    # Export assigns sheet IDs in document node order. Their public import
    # identifiers are stable even when a group is nested in another group.
    by_id = {n['id']: n for n in actual}
    mapped = {n['id']: f'visio-p1-s{i}' for i, n in enumerate(nodes, 1)}
    if len(by_id) != len(nodes) or set(by_id) != set(mapped.values()):
        raise PublicVsdxFidelityError('Identifiants des formes publiques incohérents')
    dx = dy = 0.0
    if nodes:
        first = nodes[0]
        imported_first = by_id[mapped[first['id']]]
        dx = imported_first['x'] - first['x']
        dy = imported_first['y'] - first['y']
    for source in nodes:
        target = by_id[mapped[source['id']]]
        expected_parent = mapped.get(source.get('visio_group_parent'))
        if target.get('visio_group_parent') != expected_parent:
            raise PublicVsdxFidelityError('Hiérarchie de groupe VSDX modifiée : ' + source['id'])
        if target['shape'] != source.get('shape', 'server'):
            raise PublicVsdxFidelityError('Catégorie de forme VSDX modifiée : ' + source['id'])
        from .node_geometry import node_dimensions
        sw, sh = node_dimensions(source)
        tw, th = node_dimensions(target)
        if any(abs(a - b) > tolerance for a, b in (
                (target['x'] - dx, source['x']),
                (target['y'] - dy, source['y']),
                (tw, sw), (th, sh))):
            raise PublicVsdxFidelityError('Géométrie publique VSDX modifiée : ' + source['id'])
        expected_label = source.get('label', source['id'])
        if target['label'] != expected_label:
            raise PublicVsdxFidelityError('Libellé public VSDX modifié : ' + source['id'])
    # A set would collapse two FC paths with the same endpoints. Compare
    # multiplicities so a changed/removed redundant SAN path cannot pass.
    expected_edges = Counter((mapped[e['from']], mapped[e['to']]) for e in edges)
    actual_edges = Counter((e['from'], e['to']) for e in links)
    if expected_edges != actual_edges:
        raise PublicVsdxFidelityError('Topologie ou multiplicité des connecteurs VSDX modifiée')
    # A multipath drawing can preserve topology while swapping the visible
    # FC fabric/port labels between two physical paths. Check each public
    # connector's Text, not the private OpenVisio payload or an unordered set.
    from xml.etree import ElementTree as ET
    from .parallel_geometry import display_edges
    from .connector_labels import edge_label_text
    from .vsdx import V
    try:
        with ZipFile(archive_path) as archive:
            page = ET.fromstring(archive.read('visio/pages/page1.xml'))
        public_shapes = {
            shape.get('ID'): shape
            for shape in page.findall(f'./{{{V}}}Shapes/{{{V}}}Shape')
            if shape.get('NameU') == 'OpenVisio connector'
        }
        for index, edge in enumerate(display_edges(edges, nodes), len(nodes)+1):
            shape = public_shapes.get(str(index))
            if shape is None:
                raise PublicVsdxFidelityError('Connecteur public VSDX absent : ' + edge['id'])
            text_element = shape.find(f'{{{V}}}Text')
            actual_label = ''.join(text_element.itertext()) if text_element is not None else ''
            if actual_label != edge_label_text(edge):
                raise PublicVsdxFidelityError('Libellé du connecteur public VSDX modifié : ' + edge['id'])
    except (ET.ParseError, KeyError, OSError, RuntimeError) as exc:
        raise PublicVsdxFidelityError('Texte des connecteurs publics VSDX illisible') from exc

    # Check every public static connector segment. The existing topology and
    # label checks cannot detect an elbow deleted or a path routed through
    # equipment while preserving endpoints and visible FC metadata.
    from .vsdx_connector_fidelity import (audit_connector_paths,
                                          ConnectorPathFidelityError)
    try:
        path_metrics = audit_connector_paths(page, doc, tolerance=tolerance)
    except ConnectorPathFidelityError as exc:
        raise PublicVsdxFidelityError(str(exc)) from exc

    # Page size is a fidelity property: a structurally valid VSDX can still
    # clip SAN detours or long labels.  Derive its absolute world-space origin
    # from a top-level shape's public PinX/PinY, without using private JSON.
    # A nested shape has parent-relative pins and cannot anchor the page.
    from .node_geometry import node_bounds
    from .routing import routing_scene
    from .connector_labels import layout_connector_labels
    try:
        with ZipFile(archive_path) as archive:
            pages = ET.fromstring(archive.read('visio/pages/pages.xml'))
        sheet = pages.find(f'./{{{V}}}Page/{{{V}}}PageSheet')
        values = {c.get('N'): float(c.get('V')) for c in sheet.findall(f'{{{V}}}Cell')}
        page_w, page_h = values['PageWidth'] * 96, values['PageHeight'] * 96
        if not (0 < page_w < float('inf') and 0 < page_h < float('inf')):
            raise ValueError('invalid page size')
        top = next((n for n in nodes if not n.get('visio_group_parent')), None)
        if top is not None:
            public_top = next(s for s in page.findall(f'./{{{V}}}Shapes/{{{V}}}Shape')
                              if s.get('ID') == str(nodes.index(top) + 1))
            pins = {c.get('N'): float(c.get('V')) for c in public_top.findall(f'{{{V}}}Cell')}
            page_x0 = top['x'] - pins['PinX'] * 96
            page_y0 = top['y'] - (page_h - pins['PinY'] * 96)
            extent = [node_bounds(n) for n in nodes]
            scene = routing_scene(nodes)
            for edge in display_edges(edges, nodes):
                extent.extend((x, y, x, y) for x, y in scene.route_points(edge))
            labels = layout_connector_labels(nodes, edges, scene=scene)
            extent.extend(label.bounds for label in labels.labels.values())
            slack = max(tolerance, 0.01)
            if any((x0 < page_x0 - slack or y0 < page_y0 - slack
                    or x1 > page_x0 + page_w + slack
                    or y1 > page_y0 + page_h + slack)
                   for x0, y0, x1, y1 in extent):
                raise PublicVsdxFidelityError(
                    'Dimensions de page VSDX insuffisantes : formes, routes ou libellés coupés')
    except PublicVsdxFidelityError:
        raise
    except (ET.ParseError, KeyError, OSError, StopIteration, TypeError, ValueError, AttributeError) as exc:
        raise PublicVsdxFidelityError('Dimensions de page VSDX publiques illisibles') from exc
    return {'status': 'PASS', 'scope': 'public-xml-synthetic',
            'nodes': len(nodes), 'groups': sum(n.get('shape') == 'visio-group' for n in nodes),
            'connectors': len(edges), 'route_points_checked': path_metrics['route_points_checked'],
            'tolerance_px': tolerance,
            'not_qualified': ['Microsoft Visio', 'masters', 'rotations', 'styles',
                              'formulas', 'dynamic routing', 'multi-page fidelity']}


def main():
    import argparse
    import json
    from .model import load
    parser = argparse.ArgumentParser(description='Audit VSDX public sans payload privé')
    parser.add_argument('vsdx', type=Path)
    parser.add_argument('source_ovjson', type=Path)
    args = parser.parse_args()
    print(json.dumps(audit_public_vsdx(args.vsdx, load(args.source_ovjson)),
                     ensure_ascii=False, indent=2))


if __name__ == '__main__':
    main()
