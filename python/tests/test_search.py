import unittest
from openvisio.search import find_nodes

class SearchTests(unittest.TestCase):
    def setUp(self):
        self.nodes=[
            {"id":"a","label":"Baie Pure","vendor":"Pure Storage","address":"10.1.2.3","shape":"storage"},
            {"id":"b","label":"SAN-01","hostname":"SW-PARIS","vendor":"Brocade","shape":"san-switch"},
        ]
    def test_accent_and_case(self):
        self.assertEqual([n["id"] for n in find_nodes(self.nodes,"pure")],["a"])
        self.assertEqual([n["id"] for n in find_nodes(self.nodes,"sw-paris")],["b"])
    def test_ip_and_shape(self):
        self.assertEqual([n["id"] for n in find_nodes(self.nodes,"10.1.2")],["a"])
        self.assertEqual([n["id"] for n in find_nodes(self.nodes,"san-switch")],["b"])
    def test_empty_query(self):
        self.assertEqual(find_nodes(self.nodes,"  "),[])
