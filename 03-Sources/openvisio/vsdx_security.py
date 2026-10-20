"""Untrusted VSDX ZIP/XML checks. Author: Abdelhalim Talbi."""
from pathlib import PurePosixPath

def validate_member(entry):
    name = entry.filename.replace("\\", "/")
    parts = PurePosixPath(name).parts
    if (entry.file_size > 10_000_000 or ".." in parts or name.startswith("/")
            or "\\" in entry.filename or (parts and ":" in parts[0])):
        raise ValueError("Entrée VSDX non sûre")
    if entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200:
        raise ValueError("VSDX à compression suspecte")

def reject_external_entities(xml_payload):
    upper = xml_payload.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("XML VSDX avec entités externes interdit")
