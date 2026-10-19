import unittest
from openvisio.render import node_at, edge_at, draw_document

class FakeCanvas:
    def __init__(self):
        self.calls = []
    def delete(self, *args):
        self.calls.append(("delete", args))
    def create_line(self, *args, **kwargs):
        self.calls.append(("line", args))
    def create_rectangle(self, *args, **kwargs):
        self.calls.append(("rectangle", args))
    def create_text(self, *args, **kwargs):
        self.calls.append(("text", args))

class RenderTests(unittest.TestCase):
    def setUp(self):
        self.nodes = [{"id":"a","x":100,"y":100},{"id":"b","x":300,"y":100}]
        self.edges = [{"id":"ab","from":"a","to":"b"}]
    def test_node_hit(self):
        self.assertEqual(node_at(self.nodes, 100, 100)["id"], "a")
        self.assertIsNone(node_at(self.nodes, 600, 600))
    def test_edge_hit(self):
        self.assertEqual(edge_at(self.nodes, self.edges, 200, 100)["id"], "ab")
        self.assertIsNone(edge_at(self.nodes, self.edges, 200, 130))
    def test_draw(self):
        canvas = FakeCanvas()
        draw_document(canvas, {"nodes":self.nodes,"edges":self.edges}, selected_edge="ab")
        self.assertEqual(sum(kind == "line" for kind, _ in canvas.calls), 1)
        self.assertEqual(sum(kind == "rectangle" for kind, _ in canvas.calls), 2)
