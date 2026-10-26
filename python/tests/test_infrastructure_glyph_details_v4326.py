"""V43.26 infrastructure glyph body/details contracts; no Visio stencil claim."""
import unittest

from openvisio.shape_icons import equipment_outline, equipment_detail_primitives, equipment_icon


class InfrastructureGlyphTests(unittest.TestCase):
    def test_all_catalogue_types_have_distinct_body_silhouettes(self):
        kinds = ('server', 'storage', 'san-switch', 'switch', 'network-switch',
                 'nas', 'firewall', 'database', 'application')
        outlines = []
        for index, kind in enumerate(kinds):
            node = {'id': str(index), 'shape': kind, 'x': 200.0, 'y': 120.0,
                    'width': 140.0, 'height': 60.0}
            outline = equipment_outline(node)
            self.assertIsNotNone(outline, kind)
            self.assertGreaterEqual(len(outline), 4, kind)
            outlines.append(tuple((round(x, 3), round(y, 3)) for x, y in outline))
        self.assertEqual(len(set(outlines)), len(kinds))

    def test_each_catalogue_badge_contains_internal_details(self):
        kinds = ('server', 'storage', 'san-switch', 'switch', 'network-switch',
                 'nas', 'firewall', 'database', 'application')
        for kind in kinds:
            with self.subTest(kind=kind):
                node = {'id': kind, 'shape': kind, 'x': 200.0, 'y': 120.0,
                        'width': 140.0, 'height': 60.0}
                self.assertIsNotNone(equipment_icon(node))
                details = equipment_detail_primitives(node)
                self.assertGreaterEqual(len(details), 3)
                self.assertTrue(all(item['kind'] in ('line', 'polygon') for item in details))

    def test_detail_coordinates_stay_inside_badge(self):
        node = {'id': 'fw', 'shape': 'firewall', 'x': 200.0, 'y': 120.0,
                'width': 140.0, 'height': 60.0}
        badge = equipment_icon(node)
        left, right = min(p[0] for p in badge), max(p[0] for p in badge)
        top, bottom = min(p[1] for p in badge), max(p[1] for p in badge)
        for primitive in equipment_detail_primitives(node):
            for x, y in primitive['points']:
                self.assertGreaterEqual(x, left - 1e-6)
                self.assertLessEqual(x, right + 1e-6)
                self.assertGreaterEqual(y, top - 1e-6)
                self.assertLessEqual(y, bottom + 1e-6)

    def test_unknown_group_and_tiny_shapes_keep_legacy_rectangle_fallback(self):
        cases = (
            {'id': 'g', 'shape': 'visio-group', 'x': 0.0, 'y': 0.0},
            {'id': 'u', 'shape': 'unknown-shape', 'x': 0.0, 'y': 0.0},
            {'id': 's', 'shape': 'server', 'x': 0.0, 'y': 0.0,
             'width': 60.0, 'height': 30.0},
        )
        for node in cases:
            with self.subTest(node=node['id']):
                self.assertIsNone(equipment_outline(node))
                self.assertIsNone(equipment_icon(node))
                self.assertEqual(equipment_detail_primitives(node), ())

    def test_outlines_do_not_expand_routing_or_hit_test_bounds(self):
        # Rendering is a pure projection: glyph vertices remain within the same
        # box used by node geometry, so connector endpoints are unaffected.
        node = {'id': 'storage', 'shape': 'storage', 'x': 300.0, 'y': 150.0,
                'width': 180.0, 'height': 80.0}
        outline = equipment_outline(node)
        self.assertTrue(all(210.0 <= x <= 390.0 and 110.0 <= y <= 190.0
                            for x, y in outline))


if __name__ == '__main__':
    unittest.main()
