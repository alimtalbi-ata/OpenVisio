import unittest
from openvisio.properties import normalize_properties
from openvisio.model import validate

class EquipmentMetadataTests(unittest.TestCase):
    def test_extended_metadata_roundtrip_validation(self):
        node={"id":"a","x":0,"y":0,"shape":"storage",**normalize_properties(
            label="Array-01",hostname="array01.example",address="192.0.2.10",
            vendor="Pure Storage",model="FlashArray",role="SAN primaire",
            location="Paris DC1",serial_number="SN-123",firmware="6.5.2",
            notes="Contrat support actif")}
        document=validate({"nodes":[node],"edges":[]})
        self.assertEqual(document["nodes"][0]["serial_number"],"SN-123")
        self.assertEqual(document["nodes"][0]["role"],"SAN primaire")
    def test_notes_limit(self):
        with self.assertRaises(ValueError):
            normalize_properties("array", notes="x"*2001)
    def test_invalid_ip_still_rejected(self):
        with self.assertRaises(ValueError):
            normalize_properties("array",address="192.0.2.999")
