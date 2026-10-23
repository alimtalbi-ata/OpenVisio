import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch
from zipfile import ZipFile, ZIP_DEFLATED
from openvisio.vsdx import export_vsdx, import_vsdx

class VsdxAtomicTests(unittest.TestCase):
    def test_failed_export_preserves_previous_file(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'existing.vsdx'
            p.write_bytes(b'PREVIOUS DOCUMENT')
            with patch('openvisio.vsdx.ZipFile', side_effect=OSError('disk full')):
                with self.assertRaises(OSError):
                    export_vsdx(p, {'nodes': [], 'edges': []})
            self.assertEqual(p.read_bytes(), b'PREVIOUS DOCUMENT')
            self.assertEqual(sorted(x.name for x in Path(d).iterdir()
                             if not x.name.endswith('.openvisio.lock')), ['existing.vsdx'])

    def test_case_insensitive_duplicate_zip_members_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            p = Path(d) / 'duplicate.vsdx'
            with ZipFile(p, 'w', ZIP_DEFLATED) as z:
                z.writestr('visio/pages/page1.xml', '<root/>')
                z.writestr('VISIO/PAGES/PAGE1.XML', '<root/>')
            with self.assertRaisesRegex(ValueError, 'dupliquées'):
                import_vsdx(p)
