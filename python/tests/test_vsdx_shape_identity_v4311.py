"""V43.11: neutral historical switch + explicit unknown-shape VSDX gate.

Public XML audit uses a synthetic VSDX, NOT Microsoft Visio Desktop.
Author: Abdelhalim Talbi.
"""
import copy
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from xml.etree import ElementTree as ET

from openvisio.model import save, load
from openvisio.shapes import get_shape
from openvisio.shape_icons import equipment_icon
from openvisio.vsdx import export_vsdx, import_vsdx, UnsupportedVsdxShapeError, V
from openvisio.vsdx_external import import_external_pages
from openvisio.vsdx_fidelity import audit_public_vsdx


def topology(shape="switch"):
    return {"nodes": [
        {"id": "sw", "x": 110, "y": 50, "shape": shape, "label": "Commutateur générique"},
        {"id": "san", "x": 360, "y": 30, "shape": "san-switch", "label": "Fabric A"},
        {"id": "lan", "x": 360, "y": 150, "shape": "network-switch", "label": "LAN"}],
        "edges": [
            {"id": "fc-a", "from": "sw", "to": "san", "fabric": "A", "protocol": "FC", "source_port": "0", "target_port": "1"},
            {"id": "fc-b", "from": "sw", "to": "san", "fabric": "B", "protocol": "FC", "source_port": "2", "target_port": "3"},
            {"id": "lan-link", "from": "sw", "to": "lan"}]}


class NeutralSwitchFidelity(unittest.TestCase):
    def test_neutral_switch_is_catalogued_without_san_inference(self):
        self.assertEqual(get_shape("switch")["group"], "Unclassified")
        self.assertNotEqual(get_shape("switch"), get_shape("san-switch"))
        self.assertNotEqual(get_shape("switch"), get_shape("network-switch"))
        doc = topology()
        neutral = equipment_icon(doc["nodes"][0])
        self.assertIsNotNone(neutral)
        self.assertNotEqual(neutral, equipment_icon({**doc["nodes"][0], "shape": "san-switch"}))

    def test_public_vsdx_preserves_three_switch_kinds_and_parallel_links(self):
        doc = topology()
        before = copy.deepcopy(doc)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "switches.vsdx"
            export_vsdx(path, doc)
            with ZipFile(path) as z:
                root = ET.fromstring(z.read("visio/pages/page1.xml"))
                names = [s.get("Name") for s in root.findall(f"./{{{V}}}Shapes/{{{V}}}Shape")]
                self.assertIn("OpenVisio switch", names)
                public = import_external_pages(z)
                self.assertEqual([n["shape"] for n in public["nodes"]],
                                 ["switch", "san-switch", "network-switch"])
                self.assertEqual(len(public["edges"]), 3)
            self.assertEqual(audit_public_vsdx(path, doc)["status"], "PASS")
            self.assertEqual(import_vsdx(path), doc)
        self.assertEqual(doc, before)

    def test_native_save_keeps_unknown_custom_shape_but_vsdx_rejects(self):
        doc = topology("custom-fc-device")
        with tempfile.TemporaryDirectory() as tmp:
            native, vsdx = Path(tmp) / "a.ovjson", Path(tmp) / "a.vsdx"
            save(native, doc)
            self.assertEqual(load(native)["nodes"][0]["shape"], "custom-fc-device")
            with self.assertRaisesRegex(UnsupportedVsdxShapeError, "custom-fc-device"):
                export_vsdx(vsdx, doc)
            self.assertFalse(vsdx.exists())
            self.assertFalse(list(Path(tmp).glob(".openvisio-vsdx-*")))

    def test_unknown_shape_refuses_before_overwriting_existing_export(self):
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "existing.vsdx"
            target.write_bytes(b"KEEP ORIGINAL")
            with self.assertRaisesRegex(UnsupportedVsdxShapeError, "Aucune conversion implicite"):
                export_vsdx(target, topology("mystery-device"))
            self.assertEqual(target.read_bytes(), b"KEEP ORIGINAL")
            self.assertEqual(list(Path(tmp).glob(".openvisio-vsdx-*")), [])

    def test_unknown_shape_does_not_create_output_directory(self):
        with tempfile.TemporaryDirectory() as tmp:
            folder = Path(tmp) / "not-created"
            with self.assertRaises(UnsupportedVsdxShapeError):
                export_vsdx(folder / "x.vsdx", topology("unknown"))
            self.assertFalse(folder.exists())

    def test_empty_shape_is_not_silently_rendered_as_server(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaises(UnsupportedVsdxShapeError):
                export_vsdx(Path(tmp) / "x.vsdx", topology(""))

    def test_explicit_san_and_lan_types_still_export(self):
        for kind in ("san-switch", "network-switch", "switch"):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as tmp:
                doc = topology(kind)
                path = Path(tmp) / "x.vsdx"
                export_vsdx(path, doc)
                self.assertEqual(audit_public_vsdx(path, doc)["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
