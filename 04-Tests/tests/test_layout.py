import unittest
from openvisio.layout import snap, align

class LayoutTests(unittest.TestCase):
    def test_snap(self):
        self.assertEqual(snap(29), 20)
        self.assertEqual(snap(31), 40)
    def test_invalid_spacing(self):
        with self.assertRaises(ValueError):
            snap(10, 0)
    def test_alignment(self):
        nodes = [{"id":"a","x":10,"y":20},{"id":"b","x":40,"y":80},{"id":"c","x":90,"y":200}]
        self.assertTrue(align(nodes, {"a","b"}, "y"))
        self.assertEqual(nodes[0]["y"], 50)
        self.assertEqual(nodes[1]["y"], 50)
        self.assertEqual(nodes[2]["y"], 200)
    def test_no_alignment_for_single_node(self):
        self.assertFalse(align([{"id":"a","x":1,"y":2}], {"a"}, "x"))
