"""VSDX coverage audit tests. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path
from zipfile import ZipFile
from openvisio.vsdx import export_vsdx
from openvisio.vsdx_audit import audit_vsdx


class VsdxAuditTests(unittest.TestCase):
    def test_exported_file_structural_audit(self):
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'one.vsdx'
            export_vsdx(p, {'nodes':[{'id':'a','x':20,'y':40,'label':'A'},
                                      {'id':'b','x':50,'y':60,'label':'B'}],
                            'edges':[{'id':'e','from':'a','to':'b'}]})
            report=audit_vsdx(p)
            self.assertEqual(report['source_shape_count_excluding_1d'],2)
            self.assertEqual(report['source_1d_shape_count'],1)
            self.assertEqual(report['imported_node_count'],2)
            self.assertEqual(report['imported_edge_count'],1)
            self.assertEqual(report['node_count_coverage'],1)
            self.assertFalse(report['visio_rendering_tested'])

    def test_external_multipage_audit(self):
        from test_vsdx_multipage_v426 import ExternalMultipageTests
        with tempfile.TemporaryDirectory() as d:
            p=Path(d)/'two.vsdx'
            ExternalMultipageTests()._make(p)
            report=audit_vsdx(p)
            self.assertEqual(report['page_count'],2)
            self.assertEqual(report['source_shape_count_excluding_1d'],3)
            self.assertEqual(report['imported_node_count'],3)
            self.assertEqual(report['imported_edge_count'],1)
            self.assertIn('Multiple Visio pages flattened into OpenVisio layers',report['limitations'])

if __name__=='__main__':unittest.main()
