"""Strict bidirectional mirror parity; fails on missing or extra modules.

Normalizes CRLF/LF for Windows checkouts without weakening file-list checks.
Author: Abdelhalim Talbi. Run from a clean checkout before packaging.
"""
from pathlib import Path
import hashlib

root = Path(__file__).resolve().parent
for a, b in [('03-Sources/openvisio', 'python/openvisio'),
             ('04-Tests/tests', 'python/tests')]:
    left, right = root / a, root / b
    names_left = {p.relative_to(left) for p in left.rglob('*.py')}
    names_right = {p.relative_to(right) for p in right.rglob('*.py')}
    if names_left != names_right:
        raise SystemExit('FAIL mirror file list ' + a + ': missing=' +
                         str(sorted(names_left - names_right)) +
                         ' extra=' + str(sorted(names_right - names_left)))
    for name in sorted(names_left):
        x = hashlib.sha256((left / name).read_bytes().replace(b"\r\n", b"\n")).digest()
        y = hashlib.sha256((right / name).read_bytes().replace(b"\r\n", b"\n")).digest()
        if x != y:
            raise SystemExit('FAIL mirror content ' + str(name))
    print('PASS bidirectional source parity', a, '<->', b, len(names_left), 'files')
