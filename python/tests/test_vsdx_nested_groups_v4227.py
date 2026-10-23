"""V42.27: synthetic external VSDX grouped geometry and connector regression.

These tests do not validate visual fidelity in Microsoft Visio.
Author: Abdelhalim Talbi.
"""
import math
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx import import_vsdx
from openvisio.vsdx_geometry import group_local_to_parent_inches
from openvisio.model import save, load

V = 'http://schemas.microsoft.com/office/visio/2011/1/core'


def shp(sid, px, py, width=2, height=1, *, angle=0, locx=None, locy=None,
        children='', name='Server'):
    loc = (f'<Cell N="LocPinX" V="{locx}"/>' if locx is not None else '')
    loc += (f'<Cell N="LocPinY" V="{locy}"/>' if locy is not None else '')
    return (f'<Shape ID="{sid}" NameU="{name}">'
            f'<Cell N="PinX" V="{px}"/><Cell N="PinY" V="{py}"/>'
            f'<Cell N="Width" V="{width}"/><Cell N="Height" V="{height}"/>'
            f'<Cell N="Angle" V="{angle}"/>{loc}'
            f'<Text>Equipment {sid}</Text>'
            + (f'<Shapes>{children}</Shapes>' if children else '') + '</Shape>')


def imported(shapes, connects=''):
    with tempfile.TemporaryDirectory() as d:
        p = Path(d) / 'synthetic.vsdx'
        with ZipFile(p, 'w', ZIP_DEFLATED) as z:
            z.writestr('visio/pages/page1.xml',
                       f'<PageContents xmlns="{V}"><Shapes>{shapes}</Shapes>'
                       f'<Connects>{connects}</Connects></PageContents>')
        return import_vsdx(p)


class NestedGroupsTests(unittest.TestCase):
    def test_unrotated_group_child_uses_local_coordinates(self):
        child = shp(2, 1, 1)
        doc = imported(shp(1, 10, 8, 6, 4, children=child))
        self.assertEqual(len(doc['nodes']), 2)
        node = doc['nodes'][1]
        self.assertEqual(node['x'], 8 * 96)
        self.assertEqual(node['visio_group_parent'], 'visio-p1-s1')
        self.assertEqual(doc['metadata']['group_children_imported'], 1)
        self.assertEqual(doc['metadata']['group_children_omitted'], 0)

    def test_parent_rotation_rotates_child_position_and_envelope(self):
        child = shp(2, 5, 2, 2, 1)
        doc = imported(shp(1, 10, 8, 6, 4, angle=math.pi / 2, children=child))
        node = doc['nodes'][1]
        self.assertAlmostEqual(node['x'], 10 * 96, places=3)
        self.assertAlmostEqual(node['width'], 96, places=3)
        self.assertAlmostEqual(node['height'], 192, places=3)
        self.assertEqual(doc['metadata']['rotated_shapes_as_bounding_boxes'], 2)

    def test_offcenter_group_locpin(self):
        child = shp(2, 2, 1)
        doc = imported(shp(1, 10, 8, 6, 4, locx=0, locy=0, children=child))
        self.assertEqual(doc['nodes'][1]['x'], 12 * 96)

    def test_nested_rotations_compose(self):
        leaf = shp(3, 2, 1, 2, 1)
        middle = shp(2, 3, 2, 4, 2, angle=math.pi / 2, children=leaf)
        doc = imported(shp(1, 10, 8, 6, 4, angle=math.pi / 2, children=middle))
        self.assertEqual(len(doc['nodes']), 3)
        leaf_node = doc['nodes'][2]
        self.assertAlmostEqual(leaf_node['x'], 10 * 96, places=3)
        self.assertAlmostEqual(leaf_node['width'], 2 * 96, places=3)
        self.assertAlmostEqual(leaf_node['height'], 1 * 96, places=3)
        self.assertEqual(leaf_node['visio_group_parent'], 'visio-p1-s2')
        self.assertEqual(doc['metadata']['group_children_imported'], 2)

    def test_connector_can_reference_grouped_children(self):
        children = shp(2, 1, 1) + shp(3, 4, 1)
        connections = ('<Connect FromSheet="4" FromCell="BeginX" ToSheet="2"/>'
                       '<Connect FromSheet="4" FromCell="EndX" ToSheet="3"/>')
        doc = imported(shp(1, 10, 8, 6, 4, children=children) +
                       '<Shape ID="4"><Cell N="OneD" V="1"/></Shape>', connections)
        self.assertEqual(len(doc['edges']), 1)
        self.assertEqual(doc['edges'][0]['from'], 'visio-p1-s2')
        self.assertEqual(doc['edges'][0]['to'], 'visio-p1-s3')

    def test_missing_group_dimensions_skips_child_instead_of_guessing(self):
        child = shp(2, 2, 1)
        parent = ('<Shape ID="1" NameU="Group">'
                  '<Cell N="PinX" V="10"/><Cell N="PinY" V="8"/>'
                  f'<Shapes>{child}</Shapes></Shape>')
        doc = imported(parent)
        self.assertEqual(len(doc['nodes']), 1)
        self.assertEqual(doc['metadata']['group_children_omitted'], 1)
        self.assertEqual(doc['metadata']['group_children_imported'], 0)

    def test_invalid_group_angle_skips_children(self):
        doc = imported(shp(1, 10, 8, 6, 4, angle='NaN', children=shp(2, 1, 1)))
        self.assertEqual(doc['nodes'], [])
        self.assertGreaterEqual(doc['metadata']['group_children_omitted'], 1)

    def test_local_transform_rejects_infinite_coordinate(self):
        with self.assertRaises(ValueError):
            group_local_to_parent_inches({'Width': '4', 'Height': '2',
                                          'PinX': '3', 'PinY': '4'}, float('inf'), 2)

    def test_group_metadata_survives_document_save_load(self):
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 2, 1)))
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'diagram.ovjson'
            save(p, doc)
            result = load(p)
        self.assertEqual(result['nodes'][1]['visio_group_parent'], 'visio-p1-s1')
        self.assertEqual(result['metadata']['group_children_imported'], 1)

    def test_group_children_do_not_duplicate_page_shapes(self):
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 2, 1)) + shp(3, 2, 1))
        self.assertEqual(len(doc['nodes']), 3)
        self.assertEqual(len({n['id'] for n in doc['nodes']}), 3)


if __name__ == '__main__':
    unittest.main()

class NestedGroupDefensiveTests(unittest.TestCase):
    def test_duplicate_child_sheet_is_omitted_and_reported(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 1, 1) + shp(2, 2, 1)))
        self.assertEqual(len(doc['nodes']), 2)
        self.assertEqual(doc['metadata']['group_children_omitted'], 1)

    def test_nested_child_with_invalid_geometry_is_omitted(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 1, 1, width='NaN')))
        self.assertEqual(len(doc['nodes']), 1)
        self.assertEqual(doc['metadata']['group_children_omitted'], 1)

class GroupRoutingTests(unittest.TestCase):
    def test_group_envelope_not_a_solid_orthogonal_obstacle(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        from openvisio.routing import routing_scene
        children = shp(2, 1, 1) + shp(3, 5, 1)
        doc = imported(shp(1, 10, 8, 6, 4, children=children))
        self.assertEqual(doc['nodes'][0]['shape'], 'visio-group')
        scene = routing_scene(doc['nodes'])
        self.assertIn('visio-p1-s1', dict(scene.geometry()[3].query_items((0, 0, 2000, 2000))))
        self.assertNotIn('visio-p1-s1', dict(scene.routing_obstacle_index().query_items((0, 0, 2000, 2000))))
        points = scene.route_points({'from': 'visio-p1-s2', 'to': 'visio-p1-s3',
                                     'routing': 'orthogonal'})
        self.assertGreaterEqual(len(points), 2)

    def test_group_shape_change_invalidates_routing_scene(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        from openvisio.routing import routing_scene
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 1, 1)))
        first = routing_scene(doc['nodes'])
        doc['nodes'][0]['shape'] = 'server'
        second = routing_scene(doc['nodes'])
        self.assertIsNot(first, second)

class GroupVsdxRoundTripTests(unittest.TestCase):
    def test_openvisio_embedded_payload_preserves_group_origin_metadata(self):
        from test_vsdx_nested_groups_v4227 import imported, shp
        from openvisio.vsdx import export_vsdx, import_vsdx
        doc = imported(shp(1, 10, 8, 6, 4, children=shp(2, 2, 1)))
        with tempfile.TemporaryDirectory() as d:
            path = Path(d) / 'roundtrip.vsdx'
            export_vsdx(path, doc)
            recovered = import_vsdx(path)
        self.assertEqual(recovered, doc)
        self.assertEqual(recovered['metadata']['group_children_imported'], 1)
