"""Validated diagram model, no Java or JavaScript runtime. Author: Abdelhalim Talbi."""
import json
from uuid import uuid5, NAMESPACE_URL
from pathlib import Path

from .validation import validate_document

def validate(data):
    return validate_document(data)

def load(path):
    try:
        data = json.loads(Path(path).read_text(encoding="utf-8"))
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
    path = Path(path)
    validated = validate(data)
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(prefix=".openvisio-", suffix=".tmp", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump(validated, stream, ensure_ascii=False, indent=2)
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(tmp, path)
    finally:
        if os.path.exists(tmp): os.unlink(tmp)
