"""V42.96 regression: SVG export matches the editor's visible Fabric layers.

This is a synthetic OpenVisio diagram, not a Microsoft Visio fidelity test.
Author: Abdelhalim Talbi.
"""
import os
import tempfile
import unittest
import xml.etree.ElementTree as ET
from copy import deepcopy
from pathlib import Path
from unittest.mock import patch

from openvisio.export import export_svg, to_svg
from openvisio.layers import project_visible
from openvisio.model import load, save, validate

SVG = '{http://www.w3.org/2000/svg}'


def topology():
    return validate({
        'nodes': [
            {'id': 'host', 'x': 100, 'y': 100, 'label': 'HOST-A', 'shape': 'server'},
            {'id': 'array', 'x': 500, 'y': 100, 'label': 'ARRAY-A', 'shape': 'storage'},
            {'id': 'secret', 'x': 900, 'y': 100, 'label': 'HIDDEN-ARRAY',
             'shape': 'storage', 'layer': 'fabric-B'},
        ],
        'layers': [
            {'id': 'fabric-A', 'name': 'Fabric A', 'visible': True, 'locked': True},
            {'id': 'fabric-B', 'name': 'Fabric B', 'visible': False, 'locked': False},
        ],
        'edges': [
            {'id': 'fc-A', 'from': 'host', 'to': 'array', 'layer': 'fabric-A',
             'protocol': 'FC', 'fabric': 'A', 'label': 'VISIBLE-FC-A',
             'source_port': 'hba0', 'target_port': 'fc0'},
            {'id': 'fc-B', 'from': 'host', 'to': 'array', 'layer': 'fabric-B',
             'protocol': 'FC', 'fabric': 'B', 'label': 'HIDDEN-FC-B',
             'source_port': 'hba1', 'target_port': 'fc1'},
            {'id': 'fc-to-secret', 'from': 'host', 'to': 'secret',
             'protocol': 'FC', 'fabric': 'B', 'label': 'HIDDEN-ENDPOINT'},
        ],
        'metadata': {'owner': 'SAN test'},
    })


def svg_parts(document, **options):
    root = ET.fromstring(to_svg(document, **options))
    return (root,
            root.findall(SVG + 'line') + root.findall(SVG + 'polyline'),
            [node.text for node in root.findall(SVG + 'text')])


class SvgLayerVisibilityTests(unittest.TestCase):
    def test_hidden_fabric_and_incident_edges_not_exported(self):
        doc = topology()
        before = deepcopy(doc)
        root, lines, labels = svg_parts(doc)
        self.assertEqual(len(lines), 1)
        self.assertIn('HOST-A', labels)
        self.assertIn('ARRAY-A', labels)
        self.assertIn('VISIBLE-FC-A', labels)
        self.assertNotIn('HIDDEN-ARRAY', labels)
        self.assertNotIn('HIDDEN-FC-B', labels)
        self.assertNotIn('HIDDEN-ENDPOINT', labels)
        self.assertEqual(doc, before, 'Export must not alter persisted topology')
        self.assertLess(float(root.attrib['viewBox'].split()[2]), 900)

    def test_explicit_full_export_is_opt_in(self):
        doc = topology()
        _, lines, labels = svg_parts(doc, include_hidden_layers=True)
        self.assertEqual(len(lines), 3)
        self.assertIn('HIDDEN-ARRAY', labels)
        self.assertIn('HIDDEN-FC-B', labels)
        self.assertIn('HIDDEN-ENDPOINT', labels)

    def test_hidden_all_nodes_yields_empty_canvas(self):
        doc = topology()
        doc['nodes'][0]['layer'] = 'fabric-B'
        doc['nodes'][1]['layer'] = 'fabric-B'
        root, lines, labels = svg_parts(doc)
        self.assertEqual(root.attrib['viewBox'], '0 0 800 600')
        self.assertEqual(lines, [])
        self.assertEqual(labels, [])

    def test_no_hidden_layers_remains_backward_compatible(self):
        doc = topology()
        doc['layers'][1]['visible'] = True
        self.assertEqual(to_svg(doc), to_svg(doc, include_hidden_layers=True))
        self.assertEqual(len(project_visible(doc)['edges']), 3)

    def test_export_file_matches_native_save_reload_and_keeps_hidden_data(self):
        doc = topology()
        with tempfile.TemporaryDirectory() as folder:
            native = Path(folder) / 'diagram.openvisio'
            svg_path = Path(folder) / 'diagram.svg'
            save(native, doc)
            restored = load(native)
            export_svg(svg_path, restored)
            self.assertEqual(len(restored['edges']), 3)
            self.assertEqual(len(restored['nodes']), 3)
            root = ET.parse(svg_path).getroot()
            self.assertEqual(len(root.findall(SVG + 'line') + root.findall(SVG + 'polyline')), 1)
            export_svg(svg_path, restored, include_hidden_layers=True)
            root = ET.parse(svg_path).getroot()
            self.assertEqual(len(root.findall(SVG + 'line') + root.findall(SVG + 'polyline')), 3)
            self.assertEqual(load(native), doc)

    def test_invalid_layer_state_rejected_before_export(self):
        doc = topology()
        doc['layers'][1]['visible'] = 'false'
        with self.assertRaisesRegex(ValueError, 'État de calque'):
            to_svg(doc)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1',
                     'Requires an actual Tk display (e.g. Xvfb)')
class SvgLayerVisibilityGuiTests(unittest.TestCase):
    def test_editor_export_menu_respects_hidden_fabric(self):
        from openvisio.app import Editor
        app = Editor()
        try:
            app.document = topology()
            with tempfile.TemporaryDirectory() as folder:
                target = Path(folder) / 'exported.svg'
                with patch('openvisio.app.filedialog.asksaveasfilename',
                           return_value=str(target)), \
                     patch('openvisio.app.messagebox.showerror') as error:
                    app.export_as_svg()
                    error.assert_not_called()
                root = ET.parse(target).getroot()
                self.assertEqual(len(root.findall(SVG + 'line') +
                                     root.findall(SVG + 'polyline')), 1)
                labels = [item.text for item in root.findall(SVG + 'text')]
                self.assertNotIn('HIDDEN-FC-B', labels)
                self.assertNotIn('HIDDEN-ARRAY', labels)
        finally:
            app.destroy()


if __name__ == '__main__':
    unittest.main()
