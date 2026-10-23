"""Auditable, GUI-independent diagram editing commands. Author: Abdelhalim Talbi."""
from copy import deepcopy
from uuid import uuid4
from .model import validate
from .shapes import get_shape, SHAPES

def add_equipment(document, x, y, kind="server", *, ident=None):
    """Return a validated new document and the newly created equipment ID."""
    if kind not in SHAPES:
        raise ValueError("Type d'équipement inconnu : " + str(kind))
    result = deepcopy(document)
    node_id = ident or uuid4().hex
    result["nodes"].append({"id": node_id, "x": round(x), "y": round(y),
                            "label": get_shape(kind)["label"], "shape": kind})
    validate(result)
    return result, node_id

def remove_selection(document, node_ids=(), edge_id=None):
    """Delete nodes and incident links atomically, without mutating the input."""
    result = deepcopy(document)
    ids = set(node_ids)
    result["nodes"] = [node for node in result["nodes"] if node["id"] not in ids]
    result["edges"] = [edge for edge in result["edges"] if edge["id"] != edge_id
                       and edge["from"] not in ids and edge["to"] not in ids]
    validate(result)
    return result

def connect_equipment(document, source_id, target_id, *, ident=None):
    """Create an independent physical link; parallel links have unique IDs."""
    if source_id == target_id:
        raise ValueError("Une liaison ne peut pas relier un équipement à lui-même")
    result = deepcopy(document)
    ids = {node["id"] for node in result["nodes"]}
    if source_id not in ids or target_id not in ids:
        raise ValueError("Équipement source ou cible introuvable")
    result["edges"].append({"id": ident or uuid4().hex, "from": source_id, "to": target_id})
    validate(result)
    return result
