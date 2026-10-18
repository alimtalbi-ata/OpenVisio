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

def distribute(nodes, identifiers, axis):
    """Space at least three selected nodes evenly between the outermost nodes."""
    if axis not in ("x", "y"):
        raise ValueError("Unknown distribution axis")
    ids = set(identifiers)
    selected = sorted((n for n in nodes if n["id"] in ids), key=lambda n: (n[axis], n["id"]))
    if len(selected) < 3:
        return False
    first, last = selected[0][axis], selected[-1][axis]
    step = (last - first) / (len(selected) - 1)
    changed = False
    for i, node in enumerate(selected[1:-1], start=1):
        target = first + i * step
        if node[axis] != target:
            node[axis] = target
            changed = True
    return changed

def move_group(nodes, identifiers, dx, dy, spacing=None):
    """Move selected nodes together without modifying their relative offsets."""
    ids = set(identifiers)
    selected = [node for node in nodes if node["id"] in ids]
    if not selected or (dx == 0 and dy == 0):
        return False
    if spacing is not None:
        anchor = selected[0]
        dx = snap(anchor["x"] + dx, spacing) - anchor["x"]
        dy = snap(anchor["y"] + dy, spacing) - anchor["y"]
    if dx == 0 and dy == 0:
        return False
    for node in selected:
        node["x"] += dx
        node["y"] += dy
    return True
