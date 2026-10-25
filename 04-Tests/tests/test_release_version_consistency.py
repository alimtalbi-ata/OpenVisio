"""Keep the UI/package version aligned with the Windows release contract."""
import re
import unittest
from pathlib import Path

import openvisio


class ReleaseVersionConsistencyTests(unittest.TestCase):
    def test_package_version_matches_application_titles(self):
        source = Path(openvisio.__file__).with_name("app.py").read_text(encoding="utf-8")
        titles = re.findall(r'OpenVisio (\\d+\\.\\d+\\.\\d+)', source)
        self.assertTrue(titles, "Application title must expose a semantic version")
        self.assertEqual(set(titles), {openvisio.__version__})


if __name__ == "__main__":
    unittest.main()
