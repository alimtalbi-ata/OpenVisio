"""Auditable structural VSDX import coverage (not visual fidelity certification).
Author: Abdelhalim Talbi.
"""
import argparse
import json
from pathlib import Path
from zipfile import ZipFile
from .vsdx import import_vsdx
from .vsdx_external import _pages, _parse_xml, V


def audit_vsdx(path):
    """Measure page/shape/connection coverage, disclose unsupported Visio features."""
    imported = import_vsdx(path)
    with ZipFile(path) as archive:
        embedded = 'openvisio/document.json' in archive.namelist()
        pages = _pages(archive)
        source_nodes = source_edges = groups = masters = 0
        page_summary = []
        for name, part, height in pages:
            root = _parse_xml(archive, part)
            shapes = root.findall(f'.//{{{V}}}Shapes/{{{V}}}Shape')
            one_d = 0
            for shape in shapes:
                cells = {c.get('N'): c.get('V') for c in shape.findall(f'./{{{V}}}Cell')}
                if cells.get('OneD') == '1':
                    one_d += 1
                if shape.get('Type') == 'Group':
                    groups += 1
                if shape.get('Master') or shape.get('MasterShape'):
                    masters += 1
            source_nodes += len(shapes) - one_d
            source_edges += one_d
            page_summary.append({'name': name, 'shape_count': len(shapes),
                                 'one_d_count': one_d, 'height_px': height})
    imported_nodes = len(imported['nodes'])
    imported_edges = len(imported['edges'])
    limitations = []
    if groups:
        limitations.append('Grouped shapes are not faithfully reconstructed')
    if masters:
        limitations.append('Master/stencil appearance is not reconstructed')
    if len(pages) > 1:
        limitations.append('Multiple Visio pages flattened into OpenVisio layers')
    limitations.append('Styles, text metrics, routing and Microsoft Visio rendering not certified')
    return {'source': str(Path(path).name), 'mode': 'embedded' if embedded else 'external',
            'page_count': len(pages), 'pages': page_summary,
            'source_shape_count_excluding_1d': source_nodes,
            'source_1d_shape_count': source_edges,
            'imported_node_count': imported_nodes,
            'imported_edge_count': imported_edges,
            'node_count_coverage': round(imported_nodes / source_nodes, 4) if source_nodes else None,
            'connector_count_coverage': round(imported_edges / source_edges, 4) if source_edges else None,
            'group_count': groups, 'master_references': masters,
            'limitations': limitations, 'visio_rendering_tested': False}


def main(argv=None):
    parser = argparse.ArgumentParser(description='VSDX structural coverage audit (not visual certification)')
    parser.add_argument('vsdx', help='Input VSDX file')
    parser.add_argument('--output', help='Optional JSON output path')
    args = parser.parse_args(argv)
    report = audit_vsdx(args.vsdx)
    text = json.dumps(report, ensure_ascii=False, indent=2)
    if args.output:
        Path(args.output).write_text(text + '\n', encoding='utf-8')
    else:
        print(text)
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
