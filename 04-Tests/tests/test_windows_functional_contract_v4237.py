"""Static build/CI guards; these tests do not claim native Windows execution."""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]


class WindowsFunctionalContract(unittest.TestCase):
    def test_current_build_and_documentation_versions_agree(self):
        from openvisio import __version__
        current = '.'.join(__version__.split('.')[:2])
        for file in ('02-Compilation/Build-Windows.cmd',
                     '02-Compilation/installer/OpenVisio-Python.iss',
                     '02-Compilation/scripts/package_release.py',
                     '02-Compilation/scripts/generate_docs.py',
                     '02-Compilation/scripts/verify_windows_release_v' + current.replace('.', '') + '.py'):
            self.assertIn(current, (ROOT / file).read_text(encoding='utf-8'), file)
        self.assertEqual(__version__, current + '.0')

    def test_ci_references_existing_sources_and_tests(self):
        from openvisio import __version__
        current = '.'.join(__version__.split('.')[:2])
        text = (ROOT / f'.github/workflows/openvisio-v{current}-windows.yml').read_text()
        for path in set(re.findall(r"(?:03-Sources|04-Tests)/[\w./-]+\.py", text)):
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertIn('test_release_smoke_v4237.py', text)
        self.assertIn('Smoke-Installer-Windows.ps1', text)

    def test_frozen_executable_smoke_checks_actual_document_operations(self):
        script = (ROOT / '04-Tests/Smoke-Portable-Windows.ps1').read_text()
        for value in ('OPENVISIO_SMOKE_REPORT', 'ovjson-save-reopen', 'svg-parse',
                      'vsdx-public-geometry', 'vsdx-save-reopen',
                      'packaged-executable-io-synthetic', 'WaitForExit(60000)'):
            self.assertIn(value, script)
        self.assertIn('run_smoke_from_environment', (ROOT / '03-Sources/openvisio/app.py').read_text())
        from openvisio import __version__
        current = ''.join(__version__.split('.')[:2])
        self.assertIn('release_smoke.py', (ROOT / f'02-Compilation/scripts/verify_windows_release_v{current}.py').read_text())

    def test_no_false_current_windows_binary(self):
        from openvisio import __version__
        current = '.'.join(__version__.split('.')[:2])
        self.assertFalse(any(current in p.name for p in (ROOT/'01-Application').rglob('*.exe')))


if __name__ == '__main__':
    unittest.main()
