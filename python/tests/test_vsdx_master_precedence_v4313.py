"""V43.13: external Visio generic-switch / vendor-master precedence.

Synthetic OPC fixtures, NOT Microsoft Visio Desktop fidelity evidence.
Author: Abdelhalim Talbi.
"""
import tempfile
import unittest
from pathlib import Path

from openvisio.vsdx import import_vsdx, export_vsdx
from test_vsdx_master_identity_v4312 import fixture


class ExternalMasterPrecedence(unittest.TestCase):
    def _read(self, **kwargs):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "source.vsdx"
            fixture(path, **kwargs)
            return import_vsdx(path)

    def test_generic_switch_caption_uses_brocade_master(self):
        doc = self._read(visible_name="Switch", master_name="Brocade G720")
        self.assertEqual(doc["nodes"][0]["shape"], "san-switch")

    def test_generic_switch_stencil_uses_cisco_mds_master(self):
        doc = self._read(visible_name="Switch.17", master_name="Cisco MDS 9148")
        self.assertEqual(doc["nodes"][0]["shape"], "san-switch")

    def test_generic_master_nameu_does_not_hide_vendor_model_name(self):
        doc = self._read(master_name_u="Network Switch", master_name="Brocade G720")
        self.assertEqual(doc["nodes"][0]["shape"], "san-switch")

    def test_explicit_external_network_name_is_not_reclassified(self):
        doc = self._read(visible_name="Network Switch", master_name="Brocade G720")
        self.assertEqual(doc["nodes"][0]["shape"], "network-switch")

    def test_explicit_openvisio_network_master_wins(self):
        doc = self._read(master_name_u="OpenVisio network-switch",
                         master_name="Brocade G720")
        self.assertEqual(doc["nodes"][0]["shape"], "network-switch")

    def test_unknown_master_does_not_fabricate_san_identity(self):
        doc = self._read(visible_name="Switch", master_name="Generic Switch")
        self.assertEqual(doc["nodes"][0]["shape"], "network-switch")

    def test_parallel_fabrics_roundtrip_with_generic_switch_caption(self):
        with tempfile.TemporaryDirectory() as tmp:
            source, target = Path(tmp) / "external.vsdx", Path(tmp) / "public.vsdx"
            fixture(source, visible_name="Switch", master_name="Brocade G720",
                    include_links=True)
            imported = import_vsdx(source)
            self.assertEqual(imported["nodes"][0]["shape"], "san-switch")
            self.assertEqual(len(imported["edges"]), 2)
            self.assertEqual([edge["label"] for edge in imported["edges"]],
                             ["Fabric A FC0/1", "Fabric B FC0/2"])
            export_vsdx(target, imported)
            self.assertEqual(import_vsdx(target), imported)


if __name__ == "__main__":
    unittest.main()
