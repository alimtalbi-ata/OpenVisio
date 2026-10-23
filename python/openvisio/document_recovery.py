"""Recoverable document operations without GUI dependencies. Author: Abdelhalim Talbi."""
from pathlib import Path
from .model import load

def backup_path(document_path):
    """Canonical sibling backup path, preserving the original suffix."""
    return Path(str(document_path) + ".bak")

def read_backup(document_path):
    """Validate the previous on-disk version before offering recovery."""
    backup = backup_path(document_path)
    if not backup.is_file():
        raise FileNotFoundError("Aucune sauvegarde précédente disponible")
    return load(backup)
