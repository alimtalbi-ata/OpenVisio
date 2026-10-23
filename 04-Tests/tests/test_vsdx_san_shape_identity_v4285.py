"""V42.85: external Visio SAN switch identity must not become a LAN switch.

Synthetic Visio OPC fixtures only; not Microsoft Visio desktop fidelity evidence.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

from openvisio.vsdx_external import _kind
from openvisio.vsdx import import_vsdx

V = "http://schemas.microsoft.com/office/visio/2011/1/core"


class ExternalSanShapeIdentityTests(unittest.TestCase):
    def test_explicit_san_and_fibre_channel_switches(self):
        for name in ("SAN Switch", "SAN fabric", "Switch SAN", "FC Switch",
                     "Brocade FC switch", "Fibre Channel Director",
                     "Fiber-Channel Switch"):
            with self.subTest(name=name):
                self.assertEqual(_kind(name), "san-switch")

    def test_network_switch_and_location_are_not_misclassified(self):
        for name in ("Network Switch", "Cisco Nexus Switch", "San Francisco Switch",
                     "Router", "LAN Switch"):
            with self.subTest(name=name):
                self.assertEqual(_kind(name), "network-switch")

    def test_external_page_preserves_san_kind_and_parallel_topology(self):
        page = f'''<PageContents xmlns="{V}"><Shapes>
        <Shape ID="1" NameU="SAN Switch"><Cell N="PinX" V="2"/><Cell N="PinY" V="4"/></Shape>
        <Shape ID="2" NameU="Network Switch"><Cell N="PinX" V="6"/><Cell N="PinY" V="4"/></Shape>
        <Shape ID="3"><Cell N="OneD" V="1"/><Text>Fabric A</Text></Shape>
        <Shape ID="4"><Cell N="OneD" V="1"/><Text>Fabric B</Text></Shape>
        </Shapes><Connects>
        <Connect FromSheet="3" FromCell="BeginX" ToSheet="1"/>
        <Connect FromSheet="3" FromCell="EndX" ToSheet="2"/>
        <Connect FromSheet="4" FromCell="BeginX" ToSheet="1"/>
        <Connect FromSheet="4" FromCell="EndX" ToSheet="2"/>
        </Connects></PageContents>'''
        with tempfile.TemporaryDirectory() as tmp:
            target = Path(tmp) / "san-parallel.vsdx"
            with ZipFile(target, "w", ZIP_DEFLATED) as archive:
                archive.writestr("visio/pages/page1.xml", page)
            doc = import_vsdx(target)
        self.assertEqual([n["shape"] for n in doc["nodes"]],
                         ["san-switch", "network-switch"])
        self.assertEqual(len(doc["edges"]), 2)
        self.assertEqual({edge["label"] for edge in doc["edges"]},
                         {"Fabric A", "Fabric B"})
        self.assertEqual({(edge["from"], edge["to"]) for edge in doc["edges"]},
                         {("visio-p1-s1", "visio-p1-s2")})


if __name__ == "__main__":
    unittest.main()
