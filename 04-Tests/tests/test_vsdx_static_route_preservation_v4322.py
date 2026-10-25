"""V43.22 regression coverage for preserved static VSDX waypoints.

All fixtures use the source-free public OPC page format; this is not a real
Microsoft Visio Desktop interoperability certification. Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path

from openvisio.vsdx import import_vsdx

from test_vsdx_external_orthogonal_v4315 import external_fixture, sample
from openvisio.model import validate
from openvisio.visio_route import validate_visio_route
from openvisio.routing import routing_scene


class StaticVSDXRoutePreservation(unittest.TestCase):
    def test_endpoint_move_invalidates_imported_route_and_uses_router(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            external_fixture(path, sample())
            imported = import_vsdx(path)
            edge = imported['edges'][0]
            original = routing_scene(imported['nodes']).route_points(edge)
            changed = [dict(node) for node in imported['nodes']]
            source = next(node for node in changed if node['id'] == edge['from'])
            source['x'] += 25
            rerouted = routing_scene(changed).route_points(edge)
            self.assertNotEqual(rerouted, original)

    def test_new_obstacle_invalidates_preserved_route(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'external.vsdx'
            external_fixture(path, sample())
            imported = import_vsdx(path)
            edge = imported['edges'][0]
            original = routing_scene(imported['nodes']).route_points(edge)
            vertical = next((a, b) for a, b in zip(original, original[1:])
                            if abs(a[0] - b[0]) < 1e-3 and abs(a[1] - b[1]) > 50)
            a, b = vertical
            obstacle = {'id': 'new-obstacle', 'x': a[0], 'y': (a[1] + b[1]) / 2,
                        'width': 28, 'height': 28, 'shape': 'server'}
            rerouted = routing_scene(imported['nodes'] + [obstacle]).route_points(edge)
            self.assertNotEqual(rerouted, original)
            # No generated segment may cross the new rectangle interior.
            left, right = obstacle['x'] - 14, obstacle['x'] + 14
            top, bottom = obstacle['y'] - 14, obstacle['y'] + 14
            for p, q in zip(rerouted, rerouted[1:]):
                if abs(p[0] - q[0]) < 1e-3:
                    self.assertFalse(left + 1e-3 < p[0] < right - 1e-3 and
                                     max(min(p[1], q[1]), top + 1e-3) <
                                     min(max(p[1], q[1]), bottom - 1e-3))
                elif abs(p[1] - q[1]) < 1e-3:
                    self.assertFalse(top + 1e-3 < p[1] < bottom - 1e-3 and
                                     max(min(p[0], q[0]), left + 1e-3) <
                                     min(max(p[0], q[0]), right - 1e-3))
                else:
                    self.fail('router returned a diagonal segment')

    def test_static_route_schema_rejects_nonfinite_diagonal_and_extra_fields(self):
        valid = {'schema': 1, 'source': [0, 0, 140, 60],
                 'target': [300, 200, 140, 60],
                 'points': [[70, 0], [100, 0], [100, 170], [230, 170]]}
        self.assertEqual(validate_visio_route(valid)['points'], valid['points'])
        for mutate in (
                lambda item: item['points'][1].__setitem__(1, float('nan')),
                lambda item: item['points'][1].__setitem__(1, 1),
                lambda item: item.update({'private_payload': 'not allowed'}),
                lambda item: item.update({'points': [[0, 0]]}),
        ):
            broken = {'schema': valid['schema'], 'source': list(valid['source']),
                      'target': list(valid['target']),
                      'points': [list(point) for point in valid['points']]}
            mutate(broken)
            with self.subTest(record=broken), self.assertRaises(ValueError):
                validate_visio_route(broken)

    def test_document_validator_rejects_malformed_static_route(self):
        document = sample()
        edge = document['edges'][0]
        edge['routing'] = 'orthogonal'
        edge['visio_route'] = {'schema': 1, 'source': [80, 100, 140, 60],
                               'target': [500, 300, 140, 60],
                               'points': [[150, 100], [200, 120], [430, 300]]}
        with self.assertRaisesRegex(ValueError, 'Route statique VSDX invalide'):
            validate(document)



if __name__ == "__main__":
    unittest.main()
