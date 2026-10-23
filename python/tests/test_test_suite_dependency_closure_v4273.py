"""Detect missing cross-test fixtures before Windows build; Abdelhalim Talbi."""
import ast
from pathlib import Path
import unittest


class HistoricalSuiteClosureTests(unittest.TestCase):
    def test_both_test_trees_have_all_static_fixture_imports(self):
        root = Path(__file__).resolve().parents[2]
        for folder in (root / 'python' / 'tests', root / '04-Tests' / 'tests'):
            with self.subTest(tree=str(folder.relative_to(root))):
                self.assertTrue(folder.is_dir(), f'Missing test tree: {folder}')
                files = sorted(folder.glob('test_*.py'))
                self.assertTrue(files, f'Empty test tree: {folder}')
                names = {path.stem for path in files}
                missing = set()
                for path in files:
                    parsed = ast.parse(path.read_text(encoding='utf-8'), filename=str(path))
                    for node in ast.walk(parsed):
                        if isinstance(node, ast.ImportFrom) and node.module and node.module.startswith('test_'):
                            if node.module.split('.')[0] not in names:
                                missing.add((path.name, node.module))
                        elif isinstance(node, ast.Import):
                            for alias in node.names:
                                if alias.name.startswith('test_') and alias.name.split('.')[0] not in names:
                                    missing.add((path.name, alias.name))
                self.assertFalse(missing, f'Missing historical test fixtures: {sorted(missing)}')


if __name__ == '__main__':
    unittest.main()
