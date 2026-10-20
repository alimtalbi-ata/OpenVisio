"""Prevent UI projections from modifying source documents. Author: Abdelhalim Talbi."""
import unittest
from openvisio.layers import project_visible, project_editable

class ProjectionIsolationTests(unittest.TestCase):
    def setUp(self):
        self.doc = {"nodes":[{"id":"a","x":1,"y":2,"label":"SAN"}],"edges":[],"layers":[{"id":"L","name":"Fabric","visible":True,"locked":False}],"metadata":{"site":{"name":"DC1"}}}

    def test_visible_projection_is_detached_without_hidden_layers(self):
        view = project_visible(self.doc)
        view["nodes"][0]["label"] = "MUTATED"
        view["metadata"]["site"]["name"] = "DC2"
        self.assertEqual(self.doc["nodes"][0]["label"], "SAN")
        self.assertEqual(self.doc["metadata"]["site"]["name"], "DC1")

    def test_editable_projection_is_detached_with_locked_layer(self):
        self.doc["layers"][0]["locked"] = True
        view = project_editable(self.doc)
        view["layers"][0]["name"] = "MUTATED"
        self.assertEqual(self.doc["layers"][0]["name"], "Fabric")
