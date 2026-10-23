import unittest
from openvisio.layout import distribute, move_group

class GroupLayoutTests(unittest.TestCase):
    def test_distribute_three(self):
        nodes=[{"id":"a","x":0,"y":0},{"id":"b","x":30,"y":10},{"id":"c","x":100,"y":20}]
        self.assertTrue(distribute(nodes, {"a","b","c"}, "x"))
        self.assertEqual([n["x"] for n in nodes],[0,50,100])
    def test_move_group_preserves_spacing(self):
        nodes=[{"id":"a","x":0,"y":0},{"id":"b","x":80,"y":40},{"id":"c","x":200,"y":200}]
        self.assertTrue(move_group(nodes, {"a","b"}, 25, 35, spacing=20))
        self.assertEqual((nodes[0]["x"],nodes[0]["y"]),(20,40))
        self.assertEqual((nodes[1]["x"],nodes[1]["y"]),(100,80))
        self.assertEqual((nodes[2]["x"],nodes[2]["y"]),(200,200))
    def test_noop(self):
        self.assertFalse(distribute([], [], "x"))
        self.assertFalse(move_group([], [], 1, 1))
