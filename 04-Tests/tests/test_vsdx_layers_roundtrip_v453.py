"""Integration regression for OpenVisio VSDX import/export with persistent layers."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.model import validate
from openvisio.vsdx import export_vsdx, import_vsdx
from openvisio.vsdx_consistency import inspect

class VsdxLayerRoundtripTests(unittest.TestCase):
    def test_layers_metadata_and_edges_roundtrip(self):
        document = {
            "nodes": [
                {"id": "srv", "x": 20, "y": 40, "shape": "server", "label": "Compute", "layer": "prod"},
                {"id": "san", "x": 260, "y": 40, "shape": "storage", "label": "SAN", "layer": "prod"},
            ],
            "edges": [{"id": "fc1", "from": "srv", "to": "san", "layer": "prod"}],
            "layers": [{"id": "prod", "name": "Production", "visible": True, "locked": False}],
            "metadata": {"import_format": "native", "page_count": 1},
        }
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.vsdx"
            export_vsdx(path, document)
            with ZipFile(path) as archive:
                self.assertIsNone(archive.testzip())
                self.assertIn("visio/pages/page1.xml", archive.namelist())
            self.assertEqual(inspect(path)["status"], "consistent")
            imported = import_vsdx(path)
        self.assertEqual(imported, validate(document))

    def test_corrupt_embedded_payload_is_rejected(self):
        document = {"nodes": [{"id": "n", "x": 0, "y": 0, "label": "Node"}], "edges": []}
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "test.vsdx"
            export_vsdx(path, document)
            with ZipFile(path) as archive:
                entries = {name: archive.read(name) for name in archive.namelist()}
            entries["openvisio/document.json"] = b'{"nodes":[],"edges":[]}'
            with ZipFile(path, "w") as archive:
                for name, payload in entries.items():
                    archive.writestr(name, payload)
            self.assertEqual(inspect(path)["status"], "corrupted_payload")
            with self.assertRaises(ValueError):
                import_vsdx(path)
