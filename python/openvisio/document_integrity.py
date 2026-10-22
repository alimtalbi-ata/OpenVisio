"""Integrity snapshots for recoverable documents. Author: Abdelhalim Talbi."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    digest: str
    size: int

def snapshot(path):
    """Read one complete version and fingerprint its bytes."""
    path = Path(path).resolve()
    data = path.read_bytes()
    return FileSnapshot(path, sha256(data).hexdigest(), len(data))

def verify_snapshot(expected):
    """Reject a changed/missing file rather than silently using stale data."""
    try:
        actual = snapshot(expected.path)
    except FileNotFoundError as exc:
        raise RuntimeError('La sauvegarde a disparu depuis sa vérification') from exc
    if actual.digest != expected.digest or actual.size != expected.size:
        raise RuntimeError('La sauvegarde a changé depuis sa vérification')
    return True
