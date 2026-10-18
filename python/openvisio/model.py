"""Validated diagram model, no Java or JavaScript runtime. Author: Abdelhalim Talbi."""
import json
from pathlib import Path

from .validation import validate_document

def validate(data):
    return validate_document(data)

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
