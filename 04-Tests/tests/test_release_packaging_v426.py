"""Packaging path regression. Author: Abdelhalim Talbi."""
import unittest
from pathlib import Path

class PackagingPathTests(unittest.TestCase):
    def test_release_packager_uses_canonical_paths(self):
        root = Path(__file__).resolve().parents[2]
        script = (root / '02-Compilation/scripts/package_release.py').read_text(encoding='utf-8')
        self.assertIn('03-Sources/openvisio/', script)
        self.assertIn('04-Tests/tests/', script)
        self.assertIn('file.relative_to(root / "openvisio")', script)
        self.assertIn('file.relative_to(root / "tests")', script)
