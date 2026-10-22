"""Strict diagram integrity checks. Author: Abdelhalim Talbi."""
import math
from .san_multipath import ParallelLinkIndex

def validate_document(data):
    if not isinstance(data, dict):
        raise ValueError("Le document doit être un objet JSON")
    nodes, edges = data.get("nodes", []), data.get("edges", [])
    if not isinstance(nodes, list) or not isinstance(edges, list):
        raise ValueError("Collections nodes/edges invalides")
    if len(nodes) > 100000 or len(edges) > 200000:
        raise ValueError("Document trop volumineux")
    node_ids, edge_ids, directed_pairs = set(), set(), ParallelLinkIndex()
    for node in nodes:
        if not isinstance(node, dict):
            raise ValueError("Équipement invalide")
        ident = node.get("id")
        if not isinstance(ident, str) or not ident or ident in node_ids:
            raise ValueError("Identifiant équipement invalide ou dupliqué")
        node_ids.add(ident)
        for key in ("x", "y"):
            value = node.get(key)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not math.isfinite(value):
                raise ValueError("Coordonnée invalide")
        for key in ("label", "shape", "hostname", "address", "vendor", "model", "role", "location", "serial_number", "firmware", "notes"):
            if key in node and (not isinstance(node[key], str) or len(node[key]) > 4096):
                raise ValueError("Propriété équipement invalide : " + key)
    for edge in edges:
        if not isinstance(edge, dict):
            raise ValueError("Liaison invalide")
        ident = edge.get("id")
        if not isinstance(ident, str) or not ident or ident in edge_ids or ident in node_ids:
            raise ValueError("Identifiant liaison invalide ou dupliqué")
        edge_ids.add(ident)
        source, target = edge.get("from"), edge.get("to")
        if not isinstance(source, str) or not isinstance(target, str) or source not in node_ids or target not in node_ids:
            raise ValueError("Liaison vers un équipement inexistant")
        if source == target:
            raise ValueError("Une liaison ne peut pas relier un équipement à lui-même")
        for key in ("protocol", "source_port", "target_port", "fabric", "speed_gbps", "visio_connector_sheet_id", "label"):
            if key in edge and (not isinstance(edge[key], str) or len(edge[key]) > 4096):
                raise ValueError("Propriété liaison invalide : " + key)
        directed_pairs.add(source, target, edge)
    return {"nodes": nodes, "edges": edges}
