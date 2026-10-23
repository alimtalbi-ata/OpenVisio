"""Validated diagram model, no Java or JavaScript runtime. Author: Abdelhalim Talbi."""
import json
from uuid import uuid5, NAMESPACE_URL
from pathlib import Path

from .validation import validate_document

def validate(data):
    return validate_document(data)

def load(path):
    return load_bytes(Path(path).read_bytes())

def load_bytes(payload):
    try:
        data = json.loads(payload.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ValueError("Document OpenVisio illisible ou JSON invalide") from exc
    if isinstance(data, dict) and isinstance(data.get("edges", []), list):
        # Backward compatibility with earlier diagrams lacking edge IDs.
        edges = []
        for index, edge in enumerate(data["edges"]):
            if isinstance(edge, dict) and "id" not in edge:
                key = str(index) + ":" + str(edge.get("from")) + ":" + str(edge.get("to"))
                edge = {**edge, "id": "legacy-" + uuid5(NAMESPACE_URL, key).hex}
            edges.append(edge)
        data = {**data, "edges": edges}
    return validate(data)

def save(path, data):
    import os
    import tempfile
    import shutil
    path = Path(path)
    validated = validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".openvisio-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(validated, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        # Keep the last on-disk version before atomic replacement.
        # A failed backup aborts the save without touching the original.
        if path.is_file():
            backup = path.with_name(path.name + ".bak")
            backup_fd, backup_tmp = tempfile.mkstemp(
                prefix=".openvisio-backup-", suffix=".tmp", dir=path.parent
            )
            try:
                with os.fdopen(backup_fd, "wb") as backup_stream:
                    with path.open("rb") as original:
                        shutil.copyfileobj(original, backup_stream)
                    backup_stream.flush()
                    os.fsync(backup_stream.fileno())
                os.replace(backup_tmp, backup)
            finally:
                if os.path.exists(backup_tmp):
                    os.unlink(backup_tmp)
        os.replace(tmp, path)
        # Flush the directory entry on POSIX for crash-resistant rename.
        if os.name == "posix":
            directory_fd = os.open(path.parent, os.O_RDONLY)
            try:
                os.fsync(directory_fd)
            finally:
                os.close(directory_fd)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
