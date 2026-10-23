"""Source-free packaged executable functional qualification, V42.37.

This is an opt-in *local* self-test, not a Microsoft Visio fidelity claim.
The caller supplies an absolute JSON report path via OPENVISIO_SMOKE_REPORT;
all working files are confined to a temporary directory. The normal GUI is
never started in this mode. Author: Abdelhalim Talbi.
"""
import json
import hashlib
import os
import sys
import tempfile
from pathlib import Path
from xml.etree import ElementTree as ET

from . import __version__
from .model import load, save, SaveConflict
from .document_service import open_document_with_revision
from .export import export_svg
from .vsdx import export_vsdx, import_vsdx
from .vsdx_fidelity import audit_public_vsdx


class ReleaseSmokeError(RuntimeError):
    """A packaged OpenVisio binary cannot complete its core file workflow."""


def _example_document():
    return {
        'nodes': [
            {'id': 'esxi', 'x': -140, 'y': 0, 'label': 'ESXi-01'},
            {'id': 'flash', 'x': 460, 'y': 0, 'label': 'FlashArray-01'},
            {'id': 'fabric', 'x': 150, 'y': 0, 'label': 'SAN-Fabric-A',
             'width': 150, 'height': 135},
        ],
        'edges': [
            {'id': 'path-a', 'from': 'esxi', 'to': 'flash', 'routing': 'orthogonal',
             'protocol': 'FC', 'source_port': 'vmhba1', 'target_port': 'ct0.fc1'},
            {'id': 'path-b', 'from': 'esxi', 'to': 'flash', 'routing': 'orthogonal',
             'protocol': 'FC', 'source_port': 'vmhba2', 'target_port': 'ct1.fc2'},
        ],
    }


def exercise_document_io(directory):
    """Execute real save/load, SVG, VSDX and public-XML fidelity checks."""
    folder = Path(directory)
    folder.mkdir(parents=True, exist_ok=True)
    source = _example_document()
    native = folder / 'qualify.ovjson'
    svg = folder / 'qualify.svg'
    visio = folder / 'qualify.vsdx'
    checks = []
    save(native, source, require_absent=True)
    reopened = load(native)
    if reopened != source:
        raise ReleaseSmokeError('OVJSON save/reopen mismatch')
    checks.append('ovjson-save-reopen')
    editor_doc, editor_revision = open_document_with_revision(native)
    if editor_doc != source or editor_revision != hashlib.sha256(native.read_bytes()).hexdigest():
        raise ReleaseSmokeError('Editor bounded open/revision mismatch')
    checks.append('editor-bounded-open-revision')
    export_svg(svg, reopened)
    svg_root = ET.parse(svg).getroot()
    if not svg_root.tag.endswith('svg') or len(svg_root) < 5:
        raise ReleaseSmokeError('SVG export is empty or invalid')
    checks.append('svg-parse')
    export_vsdx(visio, reopened)
    audit = audit_public_vsdx(visio, reopened)
    if audit['connectors'] != 2 or audit['route_points_checked'] <= 4:
        raise ReleaseSmokeError('Public VSDX connector path audit incomplete')
    checks.append('vsdx-public-geometry')
    restored = import_vsdx(visio)
    if restored != reopened:
        raise ReleaseSmokeError('VSDX private model round-trip mismatch')
    checks.append('vsdx-save-reopen')
    # Exercise the same no-clobber contract as the GUI, from the real EXE.
    previous_bytes = visio.read_bytes()
    try:
        export_vsdx(visio, reopened, require_absent=True)
    except SaveConflict:
        pass
    else:
        raise ReleaseSmokeError('VSDX no-clobber export unexpectedly replaced a file')
    if visio.read_bytes() != previous_bytes:
        raise ReleaseSmokeError('Rejected VSDX export changed existing bytes')
    checks.append('vsdx-no-clobber')
    if not all(path.is_file() and path.stat().st_size > 0
               for path in (native, svg, visio)):
        raise ReleaseSmokeError('A generated document is missing or empty')
    return {'status': 'PASS', 'version': __version__, 'checks': checks,
            'nodes': len(reopened['nodes']), 'connectors': len(reopened['edges']),
            'scope': ('packaged-executable-io-synthetic' if getattr(sys, 'frozen', False)
                      else 'source-io-synthetic'),
            'microsoft_visio_qualified': False}


def run_smoke_from_environment():
    """Run only with explicit report path, write machine-readable PASS/FAIL."""
    report = os.environ.get('OPENVISIO_SMOKE_REPORT')
    if report is None:
        return False
    target = Path(report)
    if not target.is_absolute():
        raise ReleaseSmokeError('OPENVISIO_SMOKE_REPORT must be absolute')
    # Do not leave synthetic files behind or overwrite user documents.
    try:
        with tempfile.TemporaryDirectory(prefix='openvisio-smoke-') as folder:
            result = exercise_document_io(folder)
    except Exception as exc:
        result = {'status': 'FAIL', 'version': __version__,
                  'error_type': type(exc).__name__, 'error': str(exc)}
    # Explicit report path is supplied by the build/qualification operator.
    # Atomic replace avoids a partially-written PASS report.
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + '.writing')
    try:
        temporary.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding='utf-8')
        os.replace(temporary, target)
    finally:
        temporary.unlink(missing_ok=True)
    if result['status'] != 'PASS':
        raise ReleaseSmokeError(result['error'])
    return True
