"""V42.30 independent VSDX public XML audit, with corruption and atomicity tests.
Author: Abdelhalim Talbi. Synthetic-only, not Microsoft Visio qualification.
"""
import copy
import json
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from unittest.mock import patch
from openvisio.group_commands import group_selection
from openvisio.model import save
from openvisio.vsdx import export_vsdx, V
from openvisio.vsdx_fidelity import audit_public_vsdx, PublicVsdxFidelityError


def sample():
    doc = {'nodes': [
        {'id': 'a', 'x': -200, 'y': 100, 'shape': 'san-switch', 'label': 'SAN A', 'width': 140, 'height': 55},
        {'id': 'b', 'x': 150, 'y': 120, 'shape': 'storage', 'label': 'Baie', 'width': 130, 'height': 90},
        {'id': 'c', 'x': 500, 'y': 190, 'shape': 'server', 'label': 'ESXi'},
        {'id': 'd', 'x': 680, 'y': 190, 'shape': 'network-switch', 'label': 'LAN'}],
        'edges': [{'id': 'ab', 'from': 'a', 'to': 'b'},
                  {'id': 'bc', 'from': 'b', 'to': 'c'},
                  {'id': 'cd', 'from': 'c', 'to': 'd'}]}
    doc, _ = group_selection(doc, {'a', 'b'}, ident='inner')
    doc, _ = group_selection(doc, {'inner', 'c'}, ident='outer')
    return doc


def alter(source, dest, modifier):
    with ZipFile(source) as src, ZipFile(dest, 'w', ZIP_DEFLATED) as dst:
        for member in src.namelist():
            payload = src.read(member)
            if member == 'visio/pages/page1.xml':
                root = ET.fromstring(payload)
                modifier(root)
                payload = ET.tostring(root, encoding='utf-8', xml_declaration=True)
            dst.writestr(member, payload)


class PublicVsdxFidelityTests(unittest.TestCase):
    def test_nested_groups_and_connectors_public_pass(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'groups.vsdx'
            export_vsdx(path, doc)
            result = audit_public_vsdx(path, doc)
        self.assertEqual((result['nodes'], result['groups'], result['connectors']), (6, 2, 3))
        self.assertEqual(result['scope'], 'public-xml-synthetic')
        self.assertIn('Microsoft Visio', result['not_qualified'])

    def test_public_geometry_tampering_rejected(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.vsdx', Path(directory)/'b.vsdx'
            export_vsdx(a, doc)
            def mutate(root):
                node = root.find(f'.//{{{V}}}Shape[@Name="OpenVisio storage"]')
                cell = next(c for c in node.findall(f'{{{V}}}Cell') if c.get('N') == 'Width')
                cell.set('V', '100')
            alter(a, b, mutate)
            with self.assertRaisesRegex(PublicVsdxFidelityError, 'Géométrie'):
                audit_public_vsdx(b, doc)

    def test_connector_topology_tampering_rejected(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.vsdx', Path(directory)/'b.vsdx'
            export_vsdx(a, doc)
            def mutate(root):
                root.find(f'./{{{V}}}Connects').remove(root.find(f'./{{{V}}}Connects/{{{V}}}Connect'))
            alter(a, b, mutate)
            with self.assertRaisesRegex(PublicVsdxFidelityError, 'Nombre|Topologie'):
                audit_public_vsdx(b, doc)

    def test_group_hierarchy_tampering_rejected(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.vsdx', Path(directory)/'b.vsdx'
            export_vsdx(a, doc)
            def mutate(root):
                outer = root.find(f'./{{{V}}}Shapes/{{{V}}}Shape[@Type="Group"]')
                inner = outer.find(f'./{{{V}}}Shapes/{{{V}}}Shape[@Type="Group"]')
                outer.find(f'./{{{V}}}Shapes').remove(inner)
                root.find(f'./{{{V}}}Shapes').append(inner)
            alter(a, b, mutate)
            with self.assertRaises(PublicVsdxFidelityError):
                audit_public_vsdx(b, doc)

    def test_public_label_tampering_rejected(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            a, b = Path(directory)/'a.vsdx', Path(directory)/'b.vsdx'
            export_vsdx(a, doc)
            def mutate(root):
                root.find(f'.//{{{V}}}Shape/{{{V}}}Text').text = 'MODIFIED'
            alter(a, b, mutate)
            with self.assertRaisesRegex(PublicVsdxFidelityError, 'Libellé'):
                audit_public_vsdx(b, doc)

    def test_failed_prepublication_audit_preserves_existing_export(self):
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'existing.vsdx'
            path.write_bytes(b'PREVIOUS-EXPORT')
            with patch('openvisio.vsdx_fidelity.audit_public_vsdx', side_effect=PublicVsdxFidelityError('fail')):
                with self.assertRaises(PublicVsdxFidelityError):
                    export_vsdx(path, doc)
            self.assertEqual(path.read_bytes(), b'PREVIOUS-EXPORT')
            self.assertEqual(list(Path(directory).glob('.openvisio-vsdx-*')), [])

    def test_empty_diagram_public_audit(self):
        doc = {'nodes': [], 'edges': []}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'empty.vsdx'
            export_vsdx(path, doc)
            self.assertEqual(audit_public_vsdx(path, doc)['nodes'], 0)

    def test_audit_does_not_mutate_document(self):
        doc = sample()
        original = copy.deepcopy(doc)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory)/'a.vsdx'
            export_vsdx(path, doc)
            audit_public_vsdx(path, doc)
        self.assertEqual(doc, original)

    def test_cli_from_ovjson(self):
        from subprocess import run
        import sys
        doc = sample()
        with tempfile.TemporaryDirectory() as directory:
            path, src = Path(directory)/'a.vsdx', Path(directory)/'a.ovjson'
            export_vsdx(path, doc)
            save(src, doc)
            process = run([sys.executable, '-m', 'openvisio.vsdx_fidelity', str(path), str(src)],
                          capture_output=True, text=True, check=True)
            self.assertEqual(json.loads(process.stdout)['status'], 'PASS')


if __name__ == '__main__':
    unittest.main()
