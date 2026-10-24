"""Check root OPC relationship required by Visio-compatible VSDX packages."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET
from openvisio.vsdx import export_vsdx

class VsdxOpcRelationshipTests(unittest.TestCase):
    def test_root_office_document_relationship(self):
        with tempfile.TemporaryDirectory() as folder:
            path = Path(folder) / "diagram.vsdx"
            export_vsdx(path, {"nodes": [], "edges": []})
            with ZipFile(path) as archive:
                root = ET.fromstring(archive.read("_rels/.rels"))
            relationships = root.findall("{http://schemas.openxmlformats.org/package/2006/relationships}Relationship")
            self.assertEqual(len(relationships), 1)
            self.assertEqual(relationships[0].get("Type"),
                             "http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument")
            self.assertEqual(relationships[0].get("Target"), "visio/document.xml")
