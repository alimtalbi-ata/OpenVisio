"""V42.92: differentiated equipment symbols, Tk capture and SVG parity.

Synthetic visual-contract tests; no Microsoft Visio Desktop fidelity claim.
Author: Abdelhalim Talbi.
"""
import unittest
from xml.etree import ElementTree as ET

from openvisio.shape_icons import equipment_icon
from openvisio.render import draw_document
from openvisio.export import to_svg
from openvisio.retained_canvas import _CaptureCanvas
from openvisio.templates import create_template


class _Canvas:
    def __init__(self): self.items = []
    def delete(self, *_): pass
    def create_rectangle(self, *a, **kw): self.items.append(('rectangle', a, kw))
    def create_line(self, *a, **kw): self.items.append(('line', a, kw))
    def create_text(self, *a, **kw): self.items.append(('text', a, kw))
    def create_polygon(self, *a, **kw): self.items.append(('polygon', a, kw))
    def winfo_width(self): return 1024
    def winfo_height(self): return 768


class ShapeIconTests(unittest.TestCase):
    def test_san_template_has_three_distinct_silhouettes(self):
        doc = create_template('SAN multipath FC (2 fabrics)')
        icons = {n['shape']: equipment_icon(n) for n in doc['nodes']}
        self.assertEqual(set(icons), {'server', 'san-switch', 'storage'})
        self.assertEqual(len({tuple((round(x, 2), round(y, 2)) for x, y in p)
                              for p in icons.values()}), 3)

    def test_canvas_and_svg_have_one_icon_per_explicit_equipment(self):
        doc = create_template('SAN multipath FC (2 fabrics)')
        canvas = _Canvas()
        draw_document(canvas, doc)
        polygons = [item for item in canvas.items if item[0] == 'polygon']
        self.assertEqual(len(polygons), 5)
        self.assertEqual(len({item[2]['tags'][0] for item in polygons}), 5)
        root = ET.fromstring(to_svg(doc))
        svg_icons = [item for item in root if item.tag.endswith('polygon')]
        self.assertEqual(len(svg_icons), 5)
        self.assertEqual({i.get('data-openvisio-node-icon') for i in svg_icons},
                         {n['id'] for n in doc['nodes']})

    def test_retained_capture_supports_stable_polygon_tag(self):
        doc = create_template('SAN multipath FC (2 fabrics)')
        capture = _CaptureCanvas(_Canvas())
        draw_document(capture, doc)
        icons = {key: item for key, item in capture.commands.items()
                 if key.endswith(':icon')}
        self.assertEqual(len(icons), 5)
        self.assertTrue(all(item.kind == 'polygon' for item in icons.values()))

    def test_small_and_legacy_nodes_keep_old_geometry(self):
        self.assertIsNone(equipment_icon({'id':'a','x':0,'y':0}))
        self.assertIsNone(equipment_icon({'id':'a','x':0,'y':0,'shape':'visio-group'}))
        self.assertIsNone(equipment_icon({'id':'a','x':0,'y':0,'shape':'server',
                                          'width':60,'height':40}))
        doc = {'nodes':[{'id':'a','x':0,'y':0,'shape':'server',
                         'width':60,'height':40}], 'edges':[]}
        canvas = _Canvas()
        draw_document(canvas, doc)
        self.assertFalse(any(kind == 'polygon' for kind, _, _ in canvas.items))


if __name__ == '__main__': unittest.main()
