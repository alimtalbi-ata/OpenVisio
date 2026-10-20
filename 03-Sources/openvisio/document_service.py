"""Document persistence service, independent of Tkinter. Author: Abdelhalim Talbi."""
from pathlib import Path
from .model import load, save
from .document_recovery import read_backup, backup_path
from .document_integrity import snapshot, verify_snapshot

def open_document(path):
    return load(path)

def save_document(path, document):
    destination = Path(path)
    save(destination, document)
    return str(destination)

def restore_previous(path):
    return read_backup(path)

def inspect_previous(path):
    backup = backup_path(path)
    before = snapshot(backup)
    from .recovery_guard import guarded_backup_read
    document = guarded_backup_read(backup, before)
    return document, before

def restore_inspected(path, expected):
    if expected.path.resolve() != backup_path(path).resolve():
        raise ValueError("Sauvegarde non associée à ce document")
    from .recovery_guard import guarded_backup_read
    return guarded_backup_read(backup_path(path), expected)
