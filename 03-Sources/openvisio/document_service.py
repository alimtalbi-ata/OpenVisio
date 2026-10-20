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
    document = read_backup(path)
    verify_snapshot(before)
    return document, before

def restore_inspected(path, expected):
    if expected.path.resolve() != backup_path(path).resolve():
        raise ValueError("Sauvegarde non associée à ce document")
    verify_snapshot(expected)
    document = read_backup(path)
    verify_snapshot(expected)
    return document
