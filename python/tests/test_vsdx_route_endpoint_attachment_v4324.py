"""V43.24 regression tests for dangling imported static VSDX routes.

Fixtures are synthetic public OPC packages; no Microsoft Visio Desktop round-
trip is claimed. Author: Abdelhalim Talbi.
"""
import unittest

from openvisio.model import validate
from openvisio.visio_route import validate_visio_route


class StaticRouteEndpointAttachmentTests(unittest.TestCase):
    def route(self):
        return {
            "schema": 1,
            "source": [0, 0, 140, 60],
            "target": [300, 200, 140, 60],
            "points": [[70, 0], [100, 0], [100, 170], [230, 170]],
        }

    def test_attached_boundary_points_are_preserved(self):
        self.assertEqual(validate_visio_route(self.route())["points"],
                         self.route()["points"])

    def test_dangling_source_endpoint_is_rejected(self):
        route = self.route()
        route["points"][0] = [500, 0]
        with self.assertRaisesRegex(ValueError, "Départ de route VSDX détaché"):
            validate_visio_route(route)

    def test_dangling_target_endpoint_is_rejected(self):
        route = self.route()
        route["points"][2] = [100, 150]
        route["points"][-1] = [230, 150]
        with self.assertRaisesRegex(ValueError, "Arrivée de route VSDX détachée"):
            validate_visio_route(route)

    def test_endpoint_may_only_differ_by_small_rounding_error(self):
        route = self.route()
        route["points"][0] = [71.5, 0]
        route["points"][-1] = [231.5, 170]
        self.assertEqual(validate_visio_route(route)["points"][0], [71.5, 0.0])

    def test_document_validation_rejects_dangling_static_route(self):
        document = {
            "nodes": [
                {"id": "src", "x": 0, "y": 0, "width": 140, "height": 60,
                 "label": "Source", "shape": "server"},
                {"id": "dst", "x": 300, "y": 200, "width": 140, "height": 60,
                 "label": "Target", "shape": "storage"},
            ],
            "edges": [{"id": "link", "from": "src", "to": "dst",
                       "protocol": "FC", "routing": "orthogonal",
                       "visio_route": {"schema": 1,
                           "source": [0, 0, 140, 60],
                           "target": [300, 200, 140, 60],
                           "points": [[500, 500], [520, 500],
                                      [520, 170], [230, 170]]}}],
        }
        with self.assertRaisesRegex(ValueError, "Route statique VSDX invalide"):
            validate(document)


if __name__ == "__main__":
    unittest.main()
