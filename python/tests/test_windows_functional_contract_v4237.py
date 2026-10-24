"""V42.94: candidate Windows contract (static only, never a native claim).

The old V42.37 test was restored in V42.93 but assumed that the historical
V42.50 release scripts were present on GitHub. They are absent from the
source checkout; that made Windows CI fail before PyInstaller was executed.
This test now checks the actual V42.93 candidate build, smoke and installer
without changing the internal 42.50.0 application version.
Author: Abdelhalim Talbi.
"""
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[2]
CANDIDATE = '42.94'
BUILD = f'02-Compilation/Build-Windows-V{CANDIDATE}-Candidate.ps1'
WORKFLOW = f'.github/workflows/openvisio-v{CANDIDATE}-windows-candidate.yml'
INSTALLER = f'02-Compilation/installer/OpenVisio-V{CANDIDATE}-Candidate.iss'
SMOKE = '04-Tests/Smoke-Portable-V42.71.ps1'
INSTALLER_SMOKE = '04-Tests/Smoke-Installer-V42.71.ps1'


class WindowsFunctionalContract(unittest.TestCase):
    def test_candidate_and_internal_versions_are_explicit(self):
        from openvisio import __version__
        self.assertEqual(__version__, '42.50.0')
        for file in (BUILD, INSTALLER, WORKFLOW):
            self.assertTrue((ROOT / file).is_file(), file)
            self.assertIn(CANDIDATE, (ROOT / file).read_text(encoding='utf-8'), file)
        iss = (ROOT / INSTALLER).read_text(encoding='utf-8')
        self.assertIn('AppVersion={#AppVersion}', iss)
        self.assertIn('#define AppVersion "42.50.0"', iss)

    def test_ci_references_existing_sources_and_tests(self):
        workflow = (ROOT / WORKFLOW).read_text(encoding='utf-8')
        build = (ROOT / BUILD).read_text(encoding='utf-8')
        self.assertIn('Build-Windows-V42.93-Candidate.ps1'.replace('42.93', CANDIDATE), workflow)
        self.assertIn('actions/checkout@v4', workflow)
        self.assertIn('windows-2022', workflow)
        self.assertIn('if-no-files-found: error', workflow)
        self.assertNotIn('continue-on-error: true', workflow)
        for path in set(re.findall(r'(?:03-Sources|04-Tests)/[\w./-]+\.py', workflow)):
            self.assertTrue((ROOT / path).is_file(), path)
        for path in (SMOKE, INSTALLER_SMOKE, INSTALLER):
            self.assertTrue((ROOT / path).is_file(), path)
        self.assertIn('python -m unittest discover', build)
        self.assertIn('python -m PyInstaller', build)
        self.assertIn('Smoke-Portable-V42.71.ps1', build)
        self.assertIn('Smoke-Installer-V42.71.ps1', build)
        self.assertIn('Get-FileHash', build)

    def test_frozen_executable_smoke_checks_actual_document_operations(self):
        script = (ROOT / SMOKE).read_text(encoding='utf-8')
        for value in ('OPENVISIO_SMOKE_REPORT', 'ovjson-save-reopen',
                      'svg-parse', 'vsdx-public-geometry', 'vsdx-save-reopen',
                      'packaged-executable-io-synthetic', 'WaitForExit(60000)',
                      'editor-bounded-open-revision'):
            self.assertIn(value, script)
        self.assertIn('run_smoke_from_environment',
                      (ROOT / '03-Sources/openvisio/app.py').read_text(encoding='utf-8'))
        installed = (ROOT / INSTALLER_SMOKE).read_text(encoding='utf-8')
        self.assertIn('Smoke-Portable-V42.71.ps1', installed)
        self.assertIn('unins000.exe', installed)

    def test_no_false_current_windows_binary(self):
        # A source-only checkout has no candidate binary. A cumulative ZIP may
        # include the two REAL CI-built binaries, but only with matching hashes.
        binaries = list((ROOT / '01-Application').rglob('*V42.94*.exe'))
        if not binaries:
            return
        import hashlib
        manifest = ROOT / '01-Application/V42.94/OpenVisio-V42.94-Source-Candidate-Windows-SHA256.txt'
        self.assertTrue(manifest.is_file(), 'Candidate binaries require CI hashes')
        expected = dict(line.split(None, 1) for line in manifest.read_text().splitlines())
        self.assertEqual(len(binaries), 2, 'Exactly portable and installer are allowed')
        for binary in binaries:
            self.assertIn(binary.name, expected.values(), binary.name)
            actual = hashlib.sha256(binary.read_bytes()).hexdigest()
            recorded = next(h for h, name in expected.items() if name == binary.name)
            self.assertEqual(actual.lower(), recorded.lower(), binary.name)


if __name__ == '__main__':
    unittest.main()
