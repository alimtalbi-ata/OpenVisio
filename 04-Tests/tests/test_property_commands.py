"""Property edits must validate before mutating any document."""
import unittest
from openvisio.property_commands import update_equipment, update_connection

class PropertyCommandTests(unittest.TestCase):
    def setUp(self):
        self.doc = {"nodes": [{"id": "a", "x": 1, "y": 2}, {"id": "b", "x": 3, "y": 4}],
                    "edges": [{"id": "e", "from": "a", "to": "b"}]}

    def test_equipment_update_is_atomic(self):
        updated = update_equipment(self.doc, "a", {"label": "NAS-01", "address": "192.0.2.10"}, "server")
        self.assertEqual(updated["nodes"][0]["label"], "NAS-01")
        self.assertNotIn("label", self.doc["nodes"][0])

    def test_bad_ip_does_not_modify_source(self):
        with self.assertRaises(ValueError):
            update_equipment(self.doc, "a", {"label": "NAS-01", "address": "not-an-ip"}, "server")
        self.assertNotIn("label", self.doc["nodes"][0])

    def test_unknown_equipment_rejected(self):
        with self.assertRaises(ValueError):
            update_equipment(self.doc, "missing", {"label": "NAS-01"}, "server")

    def test_connection_update_is_atomic(self):
        updated = update_connection(self.doc, "e", {"protocol": "FC", "speed_gbps": "32"})
        self.assertEqual(updated["edges"][0]["speed_gbps"], "32.0")
        self.assertNotIn("speed_gbps", self.doc["edges"][0])

    def test_invalid_connection_rejected(self):
        with self.assertRaises(ValueError):
            update_connection(self.doc, "e", {"protocol": "invalid"})
        self.assertNotIn("protocol", self.doc["edges"][0])
