"""Validated diagram model, no Java or JavaScript runtime. Author: Abdelhalim Talbi."""
import json
from pathlib import Path

def validate(data):
    if not isinstance(data, dict): raise ValueError("Document must be an object")
    nodes = data.get("nodes", [])
    edges = data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list): raise ValueError("Invalid collections")
    ids = set()
    for n in nodes:
        if not isinstance(n, dict) or not isinstance(n.get("id"), str) or not n["id"] or n["id"] in ids:
            raise ValueError("Invalid or duplicate node identifier")
        ids.add(n["id"])
        for key in ("x", "y"):
            if not isinstance(n.get(key), (int, float)) or isinstance(n.get(key), bool):
                raise ValueError("Invalid coordinate")
    for e in edges:
        if not isinstance(e, dict) or e.get("from") not in ids or e.get("to") not in ids:
            raise ValueError("Dangling edge")
    return {"nodes": nodes, "edges": edges}

def load(path):
    return validate(json.loads(Path(path).read_text(encoding="utf-8")))

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
