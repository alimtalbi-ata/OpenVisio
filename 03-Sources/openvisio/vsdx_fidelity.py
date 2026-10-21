"""Independent public-page VSDX fidelity gate (not a Microsoft Visio certification).

Verifies that the public XML geometry, group hierarchy, and connector topology
survive import *without* the private OpenVisio document.json payload.
Author: Abdelhalim Talbi.
"""
from pathlib import Path
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
    from .node_geometry import node_dimensions
    for source in nodes:
        target = by_id[mapped[source['id']]]
        expected_parent = mapped.get(source.get('visio_group_parent'))
        if target.get('visio_group_parent') != expected_parent:
            raise PublicVsdxFidelityError('Hiérarchie de groupe VSDX modifiée : ' + source['id'])
        if target['shape'] != source.get('shape', 'server'):
            raise PublicVsdxFidelityError('Catégorie de forme VSDX modifiée : ' + source['id'])
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
    expected_edges = {(mapped[e['from']], mapped[e['to']]) for e in edges}
    actual_edges = {(e['from'], e['to']) for e in links}
    if len(actual_edges) != len(links) or len(expected_edges) != len(edges) or expected_edges != actual_edges:
        raise PublicVsdxFidelityError('Topologie des connecteurs VSDX modifiée')
    return {'status': 'PASS', 'scope': 'public-xml-synthetic',
            'nodes': len(nodes), 'groups': sum(n.get('shape') == 'visio-group' for n in nodes),
            'connectors': len(edges), 'tolerance_px': tolerance,
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
