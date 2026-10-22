"""Rectangle selection for topology canvas. Author: Abdelhalim Talbi."""
from .node_geometry import node_half_sizes

def nodes_in_rectangle(nodes, x0, y0, x1, y1, mode="intersect"):
    """Select nodes whose actual rectangular footprint intersects the rectangle."""
    if mode not in ("intersect", "contain"):
        raise ValueError("Invalid selection mode")
    left, right = sorted((x0, x1))
    top, bottom = sorted((y0, y1))
    result = set()
    for node in nodes:
        x, y = node["x"], node["y"]
        hw, hh = node_half_sizes(node)
        nl, nr, nt, nb = x - hw, x + hw, y - hh, y + hh
        if mode == "contain":
            hit = left <= nl and nr <= right and top <= nt and nb <= bottom
        else:
            hit = nl <= right and nr >= left and nt <= bottom and nb >= top
        if hit:
            result.add(node["id"])
    return result
