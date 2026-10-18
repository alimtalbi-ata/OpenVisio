import unittest
from openvisio.model import validate

class IntegrityTests(unittest.TestCase):
    def test_duplicate_edges(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":0,"y":0}],"edges":[{"id":"e","from":"a","to":"a"},{"id":"e","from":"a","to":"a"}]})
    def test_nan_coordinates(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":float("nan"),"y":0}],"edges":[]})
    def test_infinite_coordinates(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":0,"y":float("inf")}],"edges":[]})
    def test_missing_edge_id(self):
        with self.assertRaises(ValueError):
            validate({"nodes":[{"id":"a","x":0,"y":0}],"edges":[{"from":"a","to":"a"}]})
    def test_valid_empty(self):
        self.assertEqual(validate({"nodes":[],"edges":[]}),{"nodes":[],"edges":[]})
