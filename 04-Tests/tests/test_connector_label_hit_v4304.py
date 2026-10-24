"""V43.04: clickable SAN connector captions in the Tk editor.

Synthetic interaction geometry; not Microsoft Visio Desktop qualification.
Author: Abdelhalim Talbi.
"""
import copy
import unittest

from openvisio.connector_labels import layout_connector_labels
from openvisio.model import validate
from openvisio.render import edge_at


def san_document():
    return validate({
        'nodes': [
            {'id': 'host', 'x': 0, 'y': 0, 'shape': 'server'},
            {'id': 'fabric', 'x': 400, 'y': 0, 'shape': 'san-switch'},
        ],
        'edges': [
            {'id': 'fc-a', 'from': 'host', 'to': 'fabric',
             'label': 'Fabric A / vmhba0 / Port 1'},
        ],
    })


class ConnectorCaptionSelectionTests(unittest.TestCase):
    def test_clicking_visible_caption_selects_its_physical_fc_link(self):
        doc = san_document()
        caption = layout_connector_labels(doc['nodes'], doc['edges']).labels['fc-a']
        self.assertGreater(abs(caption.y), 9)  # Not on the connector's hit strip.
        selected = edge_at(doc['nodes'], doc['edges'], caption.x, caption.y)
        self.assertIsNotNone(selected)
        self.assertEqual(selected['id'], 'fc-a')

    def test_clicking_any_interior_caption_corner_selects_link(self):
        doc = san_document()
        label = layout_connector_labels(doc['nodes'], doc['edges']).labels['fc-a']
        x0, y0, x1, y1 = label.bounds
        for x, y in ((x0 + 1, y0 + 1), (x1 - 1, y0 + 1),
                     (x0 + 1, y1 - 1), (x1 - 1, y1 - 1)):
            with self.subTest(x=x, y=y):
                selected = edge_at(doc['nodes'], doc['edges'], x, y, tolerance=2)
                self.assertIsNotNone(selected)
                self.assertEqual(selected['id'], 'fc-a')

    def test_clicking_outside_caption_and_path_selects_nothing(self):
        doc = san_document()
        self.assertIsNone(edge_at(doc['nodes'], doc['edges'], 200, 90))

    def test_selection_does_not_mutate_persisted_san_topology(self):
        doc = san_document()
        before = copy.deepcopy(doc)
        label = layout_connector_labels(doc['nodes'], doc['edges']).labels['fc-a']
        edge_at(doc['nodes'], doc['edges'], label.x, label.y)
        self.assertEqual(doc, before)


if __name__ == '__main__':
    unittest.main()
