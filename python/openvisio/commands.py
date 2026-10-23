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
    from .group_commands import group_members
    ids = group_members(result["nodes"], node_ids)
    result["nodes"] = [node for node in result["nodes"] if node["id"] not in ids]
    result["edges"] = [edge for edge in result["edges"] if edge["id"] != edge_id
                       and edge["from"] not in ids and edge["to"] not in ids]
    validate(result)
    return result

def connect_equipment(document, source_id, target_id, *, ident=None, link=None):
    """Create a link; parallel SAN paths require distinct, explicit port pairs.

    ``link`` is an optional dictionary of real connection metadata. Unqualified
    duplicate connections remain rejected by model validation.
    """
    if source_id == target_id:
        raise ValueError("Une liaison ne peut pas relier un équipement à lui-même")
    result = deepcopy(document)
    ids = {node["id"] for node in result["nodes"]}
    if source_id not in ids or target_id not in ids:
        raise ValueError("Équipement source ou cible introuvable")
    if link is not None:
        if not isinstance(link, dict) or any(key not in (
                "protocol", "source_port", "target_port", "fabric", "speed_gbps") for key in link):
            raise ValueError("Métadonnées de liaison invalides")
        from .links import normalize_link
        metadata = normalize_link(**link)
    else:
        metadata = {}
    result["edges"].append({"id": ident or uuid4().hex,
                            "from": source_id, "to": target_id, **metadata})
    validate(result)
    return result
