"""Atomic, validated property edits. Author: Abdelhalim Talbi."""
from copy import deepcopy
from .model import validate
from .properties import normalize_properties
from .links import normalize_link
from .shapes import SHAPES
from .node_geometry import checked_size


def _locked_layers(document):
    """Single source of truth for layer protection in headless edits."""
    return {layer["id"] for layer in document.get("layers", [])
            if layer.get("locked", False)}

def update_equipment(document, equipment_id, fields, shape, *, width=None, height=None):
    if shape not in SHAPES:
        raise ValueError("Type d'équipement inconnu")
    normalized = normalize_properties(**fields)
    updated = deepcopy(document)
    node = next((n for n in updated["nodes"] if n["id"] == equipment_id), None)
    if node is None:
        raise ValueError("Équipement introuvable")
    if node.get("layer") in _locked_layers(updated):
        raise ValueError("Modification interdite : calque équipement verrouillé")
    node.update(normalized)
    node["shape"] = shape
    for key, value in (("width", width), ("height", height)):
        if value is not None:
            try:
                parsed = float(value)
            except (ValueError, TypeError, OverflowError) as exc:
                raise ValueError("Dimension " + key + " invalide") from exc
            node[key] = checked_size(parsed, key)
    return validate(updated)

def update_connection(document, connection_id, fields):
    normalized = normalize_link(**fields)
    updated = deepcopy(document)
    edge = next((e for e in updated["edges"] if e["id"] == connection_id), None)
    if edge is None:
        raise ValueError("Connexion introuvable")
    locked = _locked_layers(updated)
    # Match project_editable(): an unlocked link cannot bypass a locked
    # endpoint merely because its own link layer is still editable.
    if (edge.get("layer") in locked or any(
            node["id"] in (edge["from"], edge["to"])
            and node.get("layer") in locked for node in updated["nodes"])):
        raise ValueError("Modification interdite : liaison ou équipement verrouillé")
    edge.update(normalized)
    return validate(updated)
