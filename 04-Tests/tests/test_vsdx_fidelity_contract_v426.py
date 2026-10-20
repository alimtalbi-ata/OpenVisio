"""VSDX fidelity contract. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from openvisio.vsdx import export_vsdx, import_vsdx

class VsdxFidelityContract(unittest.TestCase):
    def test_round_trip_geometry_and_connectors(self):
        doc = {"nodes": [
            {"id":"n1","x":-250.5,"y":42.25,"label":"Stockage éàç","shape":"server"},
            {"id":"n2","x":350.75,"y":-50.5,"label":"SAN & réseau","shape":"server"}],
            "edges":[{"id":"e1","from":"n1","to":"n2"}]}
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"fidelity.vsdx"
            export_vsdx(p,doc)
            actual=import_vsdx(p)
            self.assertEqual(actual["nodes"],doc["nodes"])
            self.assertEqual(actual["edges"],doc["edges"])

    def test_export_rejects_invalid_document_without_creating_file(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/"invalid.vsdx"
            with self.assertRaises((ValueError,TypeError,KeyError)):
                export_vsdx(p,{"nodes":"not a list","edges":[]})
            self.assertFalse(p.exists())
