"""V42.31: distinct physical SAN paths must survive VSDX public-page export/import.
All VSDX files in these tests are synthetic; not Microsoft Visio certification.
Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from collections import Counter
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.commands import connect_equipment, remove_selection
from openvisio.model import validate, save, load
from openvisio.vsdx import export_vsdx, V
from openvisio.vsdx_external import import_external_pages
from openvisio.vsdx_fidelity import audit_public_vsdx, PublicVsdxFidelityError


def fabric_document():
    doc = {'nodes': [
        {'id': 'host', 'x': 30, 'y': 60, 'label': 'ESXi-01', 'shape': 'server'},
        {'id': 'array', 'x': 350, 'y': 60, 'label': 'FlashArray', 'shape': 'storage'},
        {'id': 'spare', 'x': 640, 'y': 100, 'label': 'NAS', 'shape': 'nas'},
    ], 'edges': []}
    for fabric, source_port, target_port in (
            ('A', 'vmhba1', 'ct0.fc1'), ('B', 'vmhba2', 'ct1.fc1')):
        doc = connect_equipment(doc, 'host', 'array', ident=f'path-{fabric}',
                                link={'protocol': 'FC', 'source_port': source_port,
                                      'target_port': target_port, 'fabric': fabric})
    return doc


class SanMultipathTests(unittest.TestCase):
    def test_two_distinct_fabrics_accepted_and_document_unchanged(self):
        doc = fabric_document()
        before = copy.deepcopy(doc)
        self.assertEqual([e['fabric'] for e in validate(doc)['edges']], ['A', 'B'])
        self.assertEqual(doc, before)

    def test_same_ports_and_fabric_rejected_even_with_different_edge_id(self):
        doc = fabric_document()
        duplicate = dict(doc['edges'][0], id='third-path')
        with self.assertRaisesRegex(ValueError, 'dupliquée'):
            validate({**doc, 'edges': doc['edges'] + [duplicate]})

    def test_unqualified_duplicate_remains_rejected(self):
        doc = fabric_document()
        with self.assertRaisesRegex(ValueError, 'dupliquée'):
            connect_equipment(doc, 'host', 'array', ident='generic')
        basic = {**doc, 'edges': [{'id': 'one', 'from': 'host', 'to': 'array'},
                                  {'id': 'two', 'from': 'host', 'to': 'array'}]}
        with self.assertRaisesRegex(ValueError, 'dupliquée'):
            validate(basic)

    def test_ports_are_required_for_duplicate_physical_links(self):
        doc = fabric_document()
        partial = dict(doc['edges'][1], id='partial', source_port='')
        with self.assertRaisesRegex(ValueError, 'dupliquée'):
            validate({**doc, 'edges': doc['edges'] + [partial]})

    def test_vsdx_public_audit_preserves_parallel_links(self):
        doc = fabric_document()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'multipath.vsdx'
            export_vsdx(path, doc)
            with ZipFile(path) as archive:
                imported = import_external_pages(archive)
            self.assertEqual(len(imported['edges']), 2)
            self.assertEqual(len({e['visio_connector_sheet_id'] for e in imported['edges']}), 2)
            self.assertEqual(Counter((e['from'], e['to']) for e in imported['edges']),
                             {('visio-p1-s1', 'visio-p1-s2'): 2})
            audit = audit_public_vsdx(path, doc)
            self.assertEqual(audit['connectors'], 2)
            self.assertEqual(audit['status'], 'PASS')

    def test_public_connector_rewire_rejected_with_same_link_count(self):
        doc = fabric_document()
        with tempfile.TemporaryDirectory() as temp:
            original, changed = Path(temp)/'a.vsdx', Path(temp)/'b.vsdx'
            export_vsdx(original, doc)
            with ZipFile(original) as src, ZipFile(changed, 'w', ZIP_DEFLATED) as dst:
                for name in src.namelist():
                    content = src.read(name)
                    if name == 'visio/pages/page1.xml':
                        root = ET.fromstring(content)
                        connectors = root.findall(f'./{{{V}}}Connects/{{{V}}}Connect')
                        # Replace one endpoint of a redundant FC path, preserving
                        # connector and node counts. Counter must detect the change.
                        end_links = [e for e in connectors if e.get('FromCell') == 'EndX']
                        self.assertEqual(len(end_links), 2)
                        end_links[1].set('ToSheet', '3')
                        content = ET.tostring(root, encoding='utf-8', xml_declaration=True)
                    dst.writestr(name, content)
            with self.assertRaisesRegex(PublicVsdxFidelityError, 'Topologie'):
                audit_public_vsdx(changed, doc)

    def test_save_load_and_delete_preserve_distinct_path_ids(self):
        doc = fabric_document()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'fabric.ovjson'
            save(path, doc)
            loaded = load(path)
            self.assertEqual([e['id'] for e in loaded['edges']], ['path-A', 'path-B'])
            remaining = remove_selection(loaded, edge_id='path-A')
            self.assertEqual([e['id'] for e in remaining['edges']], ['path-B'])

    def test_external_vsdx_sheet_identity_must_be_unique(self):
        doc = fabric_document()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / 'paths.vsdx'
            export_vsdx(path, doc)
            with ZipFile(path) as archive:
                imported = import_external_pages(archive)
            duplicate = dict(imported['edges'][0], id='extra')
            with self.assertRaisesRegex(ValueError, 'dupliquée'):
                validate({**imported, 'edges': imported['edges'] + [duplicate]})

    def test_invalid_link_metadata_rejected_without_mutating_source(self):
        doc = fabric_document()
        original = copy.deepcopy(doc)
        with self.assertRaisesRegex(ValueError, 'Métadonnées'):
            connect_equipment(doc, 'host', 'array', link={'fabric': 'C', 'invented': 'x'})
        self.assertEqual(doc, original)


if __name__ == '__main__':
    unittest.main()
