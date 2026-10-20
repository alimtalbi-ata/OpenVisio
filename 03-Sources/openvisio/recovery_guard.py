"""Read recovery content exactly once and validate its fingerprint.
Author: Abdelhalim Talbi.
"""
import json
from hashlib import sha256
from pathlib import Path
from .model import validate
from .document_integrity import FileSnapshot

def guarded_backup_read(path, expected):
    target = Path(path).resolve()
    if target != expected.path.resolve():
        raise ValueError("Sauvegarde non associée à ce document")
    try:
        payload = target.read_bytes()
    except FileNotFoundError as exc:
        raise RuntimeError("La sauvegarde a disparu depuis sa vérification") from exc
    if len(payload) != expected.size or sha256(payload).hexdigest() != expected.digest:
        raise RuntimeError("La sauvegarde a changé depuis sa vérification")
    try:
        document = json.loads(payload.decode("utf-8"))
    except (UnicodeError, json.JSONDecodeError) as exc:
        raise ValueError("Sauvegarde JSON invalide") from exc
    return validate(document)
