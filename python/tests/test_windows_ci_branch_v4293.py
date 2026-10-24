"""Static V42.93 Windows CI wiring and artifact contract; no native build claim.
Author: Abdelhalim Talbi.
"""
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[2]
BRANCH = 'develop/v42.93-blank-san-label-windows-20261024'


class WindowsCiContractTests(unittest.TestCase):
    def test_push_branch_and_dispatch_match_candidate(self):
        workflow = (ROOT / '.github/workflows/openvisio-v42.93-windows-candidate.yml').read_text()
        self.assertIn(f"branches: ['{BRANCH}']", workflow)
        self.assertIn('workflow_dispatch:', workflow)
        self.assertIn('runs-on: windows-2022', workflow)
        self.assertIn('Build-Windows-V42.93-Candidate.ps1', workflow)

    def test_build_produces_expected_named_artifacts(self):
        build = (ROOT / '02-Compilation/Build-Windows-V42.93-Candidate.ps1').read_text()
        iss = (ROOT / '02-Compilation/installer/OpenVisio-V42.93-Candidate.iss').read_text()
        for suffix in ('Windows-x64-Portable.exe', 'Setup-x64.exe'):
            self.assertIn('V42.93-Source-Candidate-', build + iss)
            self.assertIn(suffix, build + iss)
        self.assertIn('unittest discover', build)
        self.assertIn('Smoke-Portable', build)
        self.assertIn('Smoke-Installer', build)
        self.assertIn('Get-FileHash', build)

    def test_independent_checkout_checks_motor_sha_and_tests(self):
        script = (ROOT / '02-Compilation/Verify-GitHub-Checkout-V42.93.ps1').read_text()
        for value in (BRANCH, 'git clone --single-branch', 'model.py', 'vsdx.py',
                      'render.py', 'connector_labels.py',
                      'test_connector_blank_label_v4293.py', 'unittest discover'):
            self.assertIn(value, script)
        self.assertNotIn('REPLACE_', script)


if __name__ == '__main__':
    unittest.main()
