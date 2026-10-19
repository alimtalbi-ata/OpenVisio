"""Document persistence service, independent of Tkinter. Author: Abdelhalim Talbi."""
from pathlib import Path
from .model import load, save
from .document_recovery import read_backup

def open_document(path):
    """Validate and load a document without changing editor state."""
    return load(path)

def save_document(path, document):
    """Persist validated document and return its normalized destination."""
    destination = Path(path)
    save(destination, document)
    return str(destination)

def restore_previous(path):
    """Read and validate the previous saved version without modifying the primary file."""
    return read_backup(path)
