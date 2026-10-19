import unittest
from openvisio.selection import nodes_in_rectangle

class RectangleSelectionTests(unittest.TestCase):
    def setUp(self):
        self.nodes=[{"id":"a","x":100,"y":100},{"id":"b","x":400,"y":300}]
    def test_reversed_rectangle(self):
        self.assertEqual(nodes_in_rectangle(self.nodes,200,160,0,0),{"a"})
    def test_intersection(self):
        self.assertEqual(nodes_in_rectangle(self.nodes,160,110,180,130),{"a"})
    def test_containment(self):
        self.assertEqual(nodes_in_rectangle(self.nodes,160,110,180,130,mode="contain"),set())
        self.assertEqual(nodes_in_rectangle(self.nodes,0,0,200,200,mode="contain"),{"a"})
    def test_invalid_mode(self):
        with self.assertRaises(ValueError):
            nodes_in_rectangle(self.nodes,0,0,1,1,mode="invalid")
