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
    locked_layers = {layer["id"] for layer in result.get("layers", [])
                     if layer.get("locked", False)}
    by_id = {node["id"]: node for node in result["nodes"]}
    if any(by_id[ident].get("layer") in locked_layers for ident in ids):
        raise ValueError("Suppression interdite : calque verrouillé")
    removed_edges = [edge for edge in result["edges"]
                     if edge["id"] == edge_id or edge["from"] in ids or edge["to"] in ids]
    # Removing an unlocked node must not silently remove a protected link,
    # including a link whose layer is unlocked but touches a locked endpoint.
    if any(edge.get("layer") in locked_layers
           or by_id[edge["from"]].get("layer") in locked_layers
           or by_id[edge["to"]].get("layer") in locked_layers
           for edge in removed_edges):
        raise ValueError("Suppression interdite : liaison sur calque verrouillé")
    removed_edge_ids = {edge["id"] for edge in removed_edges}
    result["nodes"] = [node for node in result["nodes"] if node["id"] not in ids]
    result["edges"] = [edge for edge in result["edges"]
                       if edge["id"] not in removed_edge_ids]
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
    locked_layers = {layer["id"] for layer in result.get("layers", [])
                     if layer.get("locked", False)}
    if any(node["id"] in (source_id, target_id)
           and node.get("layer") in locked_layers for node in result["nodes"]):
        raise ValueError("Connexion interdite : équipement sur calque verrouillé")
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
