"""Place equipment without stacking shapes. Author: Abdelhalim Talbi."""

def next_free_position(center, nodes, *, step_x=180, step_y=100, clearance_x=145, clearance_y=65, max_rings=60):
    """Choose a non-overlapping position near the visible canvas centre."""
    cx, cy = center
    occupied = [(node["x"], node["y"]) for node in nodes]
    for ring in range(max_rings + 1):
        for gy in range(-ring, ring + 1):
            for gx in range(-ring, ring + 1):
                if ring and max(abs(gx), abs(gy)) != ring:
                    continue
                x, y = round(cx + gx * step_x), round(cy + gy * step_y)
                if all(abs(x-px) >= clearance_x or abs(y-py) >= clearance_y for px, py in occupied):
                    return x, y
    raise ValueError("Aucune position libre trouvée dans le diagramme")
