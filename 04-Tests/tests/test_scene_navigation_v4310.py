"""V43.10: zoom/fit must expose full SAN labels and routes.

Synthetic navigation tests, not Microsoft Visio Desktop fidelity.
Author: Abdelhalim Talbi.
"""
import os
import unittest

from openvisio.connector_labels import layout_connector_labels
from openvisio.viewport import MIN_ZOOM, Viewport


def san_diagram():
    nodes = [
        {'id': 'hba', 'x': 0, 'y': 0, 'shape': 'server'},
        {'id': 'array', 'x': 160, 'y': 0, 'shape': 'storage'},
    ]
    edges = [
        {'id': 'fc-a', 'from': 'hba', 'to': 'array', 'protocol': 'FC',
         'routing': 'orthogonal',
         'label': 'Fabric A · HBA0/0 ↔ Switch F-port 24 · ' + 'X' * 35},
    ]
    return nodes, edges


class SceneNavigationTests(unittest.TestCase):
    def test_wheel_zoom_out_reaches_minimum_without_fit_first(self):
        view = Viewport()
        for _ in range(80):
            view.zoom_at(1 / 1.12, 310, 175)
        self.assertAlmostEqual(view.zoom, MIN_ZOOM)
        self.assertLess(view.zoom, 0.2)

    def test_zoom_out_preserves_pointer_anchor_at_low_zoom(self):
        view = Viewport(1.0, 130, -50)
        anchor = view.world(450, 210)
        for _ in range(75):
            view.zoom_at(1 / 1.12, 450, 210)
            self.assertAlmostEqual(view.world(450, 210)[0], anchor[0], places=6)
            self.assertAlmostEqual(view.world(450, 210)[1], anchor[1], places=6)
        self.assertEqual(view.zoom, MIN_ZOOM)

    def test_fit_scene_includes_long_san_caption_in_margin(self):
        nodes, edges = san_diagram()
        labels = layout_connector_labels(nodes, edges)
        self.assertIn('fc-a', labels.labels)
        view = Viewport()
        view.fit_scene(nodes, edges, 600, 300, margin=30)
        for x0, y0, x1, y1 in [labels.labels['fc-a'].bounds]:
            self.assertGreaterEqual(view.screen(x0, y0)[0], 30 - 1e-6)
            self.assertGreaterEqual(view.screen(x0, y0)[1], 30 - 1e-6)
            self.assertLessEqual(view.screen(x1, y1)[0], 570 + 1e-6)
            self.assertLessEqual(view.screen(x1, y1)[1], 270 + 1e-6)

    def test_fit_scene_keeps_all_route_vertices_inside_view(self):
        from openvisio.routing import routing_scene
        from openvisio.parallel_geometry import display_edges
        nodes, edges = san_diagram()
        view = Viewport()
        view.fit_scene(nodes, edges, 600, 300, margin=30)
        scene = routing_scene(nodes)
        for edge in display_edges(edges, nodes):
            for x, y in scene.route_points(edge):
                sx, sy = view.screen(x, y)
                self.assertGreaterEqual(sx, 30 - 1e-6)
                self.assertLessEqual(sx, 570 + 1e-6)
                self.assertGreaterEqual(sy, 30 - 1e-6)
                self.assertLessEqual(sy, 270 + 1e-6)


@unittest.skipUnless(os.environ.get('OPENVISIO_GUI_TESTS') == '1', 'Requires Tk display')
class SceneNavigationTkTests(unittest.TestCase):
    def test_editor_zoom_and_fit_use_full_scene(self):
        from openvisio.app import Editor
        editor = Editor()
        try:
            editor.update_idletasks()
            nodes, edges = san_diagram()
            editor.document = {'nodes': nodes, 'edges': edges}
            editor.history.reset(editor.document)
            editor.fit_view()
            self.assertLess(editor.viewport.zoom, 4.0)
            for _ in range(20):
                editor.zoom_center(1 / 1.2)
            self.assertLess(editor.viewport.zoom, 0.2)
        finally:
            editor.destroy()


if __name__ == '__main__':
    unittest.main()
