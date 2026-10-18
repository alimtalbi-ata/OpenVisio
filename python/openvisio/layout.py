"""Grid snapping and alignment operations for diagrams. Author: Abdelhalim Talbi."""

def snap(value, spacing=20):
    if spacing <= 0:
        raise ValueError("Grid spacing must be positive")
    return round(value / spacing) * spacing

def align(nodes, identifiers, axis, mode="center"):
    if axis not in ("x", "y"):
        raise ValueError("Unknown alignment axis")
    selected = [node for node in nodes if node["id"] in set(identifiers)]
    if len(selected) < 2:
        return False
    values = [node[axis] for node in selected]
    if mode == "min":
        target = min(values)
    elif mode == "max":
        target = max(values)
    elif mode == "center":
        target = sum(values) / len(values)
    else:
        raise ValueError("Unknown alignment mode")
    for node in selected:
        node[axis] = target
    return True
