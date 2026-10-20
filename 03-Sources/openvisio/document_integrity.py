"""Stable recovery snapshots. Author: Abdelhalim Talbi."""
from dataclasses import dataclass
from hashlib import sha256
from pathlib import Path

@dataclass(frozen=True)
class FileSnapshot:
    path: Path
    digest: str
    size: int

def snapshot(path):
    path = Path(path).resolve()
    data = path.read_bytes()
    return FileSnapshot(path, sha256(data).hexdigest(), len(data))

def verify_snapshot(expected):
    try:
        actual = snapshot(expected.path)
    except FileNotFoundError as exc:
        raise RuntimeError("La sauvegarde a disparu depuis sa vérification") from exc
    if (actual.digest, actual.size) != (expected.digest, expected.size):
        raise RuntimeError("La sauvegarde a changé depuis sa vérification")
    return True
