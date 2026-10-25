"""V43.14: preserve Visio SAN links using BeginY/EndY glue rows.

Synthetic OPC/VSDX fixtures only; not Microsoft Visio Desktop certification.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from xml.etree import ElementTree as ET
from zipfile import ZipFile

from openvisio.vsdx import import_vsdx, export_vsdx
from openvisio.vsdx_external import V
from test_vsdx_master_identity_v4312 import fixture


class ExternalVisioYAnchorConnections(unittest.TestCase):
    def _read(self, *, from_cells=("BeginY", "EndY"), duplicate=None,
              orphan=False, equipment_source=False):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "external.vsdx"
            fixture(path, include_links=True, master_name="Brocade G720")
            with ZipFile(path) as source:
                members = {name: source.read(name) for name in source.namelist()}
            page = ET.fromstring(members["visio/pages/page1.xml"])
            connects = page.find(f"{{{V}}}Connects")
            for row in connects.findall(f"{{{V}}}Connect"):
                if row.get("FromCell") == "BeginX":
                    row.set("FromCell", from_cells[0])
                elif row.get("FromCell") == "EndX":
                    row.set("FromCell", from_cells[1])
            if duplicate is not None:
                ET.SubElement(connects, f"{{{V}}}Connect", {
                    "FromSheet": "101", "FromCell": "BeginX",
                    "ToSheet": str(duplicate), "ToCell": "PinX"})
            if orphan:
                connects.findall(f"{{{V}}}Connect")[0].set("ToSheet", "999")
            if equipment_source:
                connects.findall(f"{{{V}}}Connect")[0].set("FromSheet", "1")
            members["visio/pages/page1.xml"] = ET.tostring(page, encoding="utf-8")
            with ZipFile(path, "w") as archive:
                for name, content in members.items():
                    archive.writestr(name, content)
            if duplicate == 2 or orphan or equipment_source:
                return import_vsdx(path)
            imported = import_vsdx(path)
            target = Path(tmp) / "roundtrip.vsdx"
            export_vsdx(target, imported)
            self.assertEqual(import_vsdx(target), imported)
            return imported

    def test_y_only_rows_keep_two_parallel_fabric_connections(self):
        doc = self._read()
        self.assertEqual(len(doc["edges"]), 2)
        self.assertEqual([edge["label"] for edge in doc["edges"]],
                         ["Fabric A FC0/1", "Fabric B FC0/2"])
        self.assertEqual(doc["nodes"][0]["shape"], "san-switch")

    def test_mixed_begin_y_end_x_rows_keep_topology(self):
        doc = self._read(from_cells=("BeginY", "EndX"))
        self.assertEqual(len(doc["edges"]), 2)
        self.assertEqual({edge["from"] for edge in doc["edges"]}, {"visio-p1-s1"})
        self.assertEqual({edge["to"] for edge in doc["edges"]}, {"visio-p1-s2"})

    def test_same_endpoint_glued_on_both_axes_is_idempotent(self):
        doc = self._read(duplicate=1)
        self.assertEqual(len(doc["edges"]), 2)

    def test_conflicting_x_and_y_glue_targets_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "ambigu"):
            self._read(duplicate=2)

    def test_y_only_orphan_target_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "extrémité SAN absente"):
            self._read(orphan=True)

    def test_y_only_device_cannot_impersonate_connector(self):
        with self.assertRaisesRegex(ValueError, "équipement utilisé comme connecteur"):
            self._read(equipment_source=True)


if __name__ == "__main__":
    unittest.main()
