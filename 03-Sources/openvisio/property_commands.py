"""Atomic, validated property edits. Author: Abdelhalim Talbi."""
from copy import deepcopy
from .model import validate
from .properties import normalize_properties
from .links import normalize_link
from .shapes import SHAPES

def update_equipment(document, equipment_id, fields, shape):
    if shape not in SHAPES:
        raise ValueError("Type d'équipement inconnu")
    normalized = normalize_properties(**fields)
    updated = deepcopy(document)
    node = next((n for n in updated["nodes"] if n["id"] == equipment_id), None)
    if node is None:
        raise ValueError("Équipement introuvable")
    node.update(normalized)
    node["shape"] = shape
    return validate(updated)

def update_connection(document, connection_id, fields):
    normalized = normalize_link(**fields)
    updated = deepcopy(document)
    edge = next((e for e in updated["edges"] if e["id"] == connection_id), None)
    if edge is None:
        raise ValueError("Connexion introuvable")
    edge.update(normalized)
    return validate(updated)
