"""Windows Explorer/CLI diagram opening and verifiable startup evidence.

No UI dependencies: path parsing is testable on Linux and Windows. A receipt
is emitted only when an operator explicitly sets OPENVISIO_STARTUP_REPORT.
The receipt is not evidence of Microsoft Visio fidelity.
Author: Abdelhalim Talbi.
"""
import json
import os
import sys
import tempfile
from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class StartupTarget:
    path: Path
    kind: str


def parse_startup_target(arguments):
    """Accept zero or one existing OVJSON/JSON/VSDX document from Explorer.

    Do not silently ignore extra arguments or treat options as filenames.
    Never create a missing file as a side effect of starting the editor.
    """
    args = list(arguments)
    if not args:
        return None
    if len(args) != 1 or not isinstance(args[0], str) or args[0].startswith('--'):
        raise ValueError('OpenVisio attend un seul chemin de diagramme, sans option')
    path = Path(args[0]).expanduser()
    if path.suffix.lower() not in ('.ovjson', '.json', '.vsdx'):
        raise ValueError('Format de lancement non pris en charge : OVJSON, JSON ou VSDX attendu')
    try:
        path = path.resolve(strict=True)
    except OSError as exc:
        raise ValueError('Le diagramme demandé est introuvable') from exc
    if not path.is_file():
        raise ValueError('Le chemin fourni ne désigne pas un fichier')
    return StartupTarget(path, 'vsdx' if path.suffix.lower() == '.vsdx' else 'ovjson')


def write_startup_receipt(target, opened, document, *, report_path=None):
    """Record a real GUI document-load result for Windows smoke qualification.

    The explicit report is atomically published and never embeds the user's
    document content. The report must not overwrite the opened diagram.
    """
    if report_path is None:
        report_path = os.environ.get('OPENVISIO_STARTUP_REPORT')
    if not report_path:
        return False
    destination = Path(report_path)
    if not destination.is_absolute():
        raise ValueError('OPENVISIO_STARTUP_REPORT doit être absolu')
    if destination.resolve() == target.path.resolve():
        raise ValueError('Le rapport ne peut pas remplacer le diagramme')
    from . import __version__
    report = {
        'status': 'PASS' if opened else 'FAIL',
        'version': __version__,
        'mode': target.kind,
        'filename': target.path.name,
        'nodes': len(document.get('nodes', [])) if opened else 0,
        'connectors': len(document.get('edges', [])) if opened else 0,
        'scope': 'packaged-gui-file-open' if getattr(sys, 'frozen', False)
                 else 'source-gui-file-open',
        'microsoft_visio_qualified': False,
    }
    destination.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix='.openvisio-startup-', suffix='.tmp', dir=destination.parent)
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as stream:
            json.dump(report, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(temporary, destination)
    finally:
        if os.path.exists(temporary):
            os.unlink(temporary)
    return True
