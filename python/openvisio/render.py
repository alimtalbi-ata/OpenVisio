"""Canvas rendering and geometry, independent from editor state. Author: Abdelhalim Talbi."""
from math import hypot
from .shapes import get_shape

NODE_HALF_WIDTH = 70
NODE_HALF_HEIGHT = 30

def node_at(nodes, x, y):
    for node in reversed(nodes):
        if abs(node["x"] - x) <= NODE_HALF_WIDTH and abs(node["y"] - y) <= NODE_HALF_HEIGHT:
            return node
    return None

def edge_at(nodes, edges, x, y, tolerance=9):
    by_id = {n["id"]: n for n in nodes}
    for edge in reversed(edges):
        a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
        if not a or not b:
            continue
        dx, dy = b["x"] - a["x"], b["y"] - a["y"]
        length_sq = dx * dx + dy * dy
        if not length_sq:
            continue
        t = max(0, min(1, ((x - a["x"]) * dx + (y - a["y"]) * dy) / length_sq))
        if hypot(x - (a["x"] + t * dx), y - (a["y"] + t * dy)) <= tolerance:
            return edge
    return None

def draw_document(canvas, document, selected_node=None, selected_edge=None):
    import tkinter as tk
    canvas.delete("all")
    by_id = {n["id"]: n for n in document["nodes"]}
    for edge in document["edges"]:
        a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
        if a and b:
            selected = edge.get("id") == selected_edge
            canvas.create_line(a["x"], a["y"], b["x"], b["y"], fill="#dc2626" if selected else "#2563eb", width=4 if selected else 2, arrow=tk.LAST)
    for node in document["nodes"]:
        x, y = node["x"], node["y"]
        selected = node["id"] == selected_node
        canvas.create_rectangle(x-70, y-30, x+70, y+30, fill="#bfdbfe" if selected else get_shape(node.get("shape", "server"))["fill"], outline="#1d4ed8", width=3 if selected else 1)
        canvas.create_text(x, y, text=node.get("label", "Équipement")[:40], fill="#172554")
