"""Single-read recovery verification. Author: Abdelhalim Talbi."""
from hashlib import sha256
from pathlib import Path
from .model import load_bytes

def guarded_backup_read(path, expected):
    target = Path(path).resolve()
    if target != expected.path.resolve():
        raise ValueError('Sauvegarde non associée à ce document')
    try:
        payload = target.read_bytes()
    except FileNotFoundError as exc:
        raise RuntimeError('La sauvegarde a disparu depuis sa vérification') from exc
    if len(payload) != expected.size or sha256(payload).hexdigest() != expected.digest:
        raise RuntimeError('La sauvegarde a changé depuis sa vérification')
    return load_bytes(payload)
