"""Group-safe alignment/distribution for infrastructure diagrams.

Groups and descendants use absolute document coordinates. Author: Abdelhalim Talbi.
"""


def snap(value, spacing=20):
    if spacing <= 0:
        raise ValueError("Grid spacing must be positive")
    return round(value / spacing) * spacing


def _selection_roots(nodes, identifiers):
    ids = set(identifiers)
    by_id = {node["id"]: node for node in nodes}
    roots = []
    for node in nodes:
        if node["id"] not in ids:
            continue
        ancestor = node.get("visio_group_parent")
        visited = set()
        while ancestor is not None and ancestor not in visited:
            if ancestor in ids:
                break
            visited.add(ancestor)
            ancestor = by_id.get(ancestor, {}).get("visio_group_parent")
        else:
            roots.append(node)
    return roots


def _translate_subtrees(nodes, shifts, axis):
    children = {}
    for node in nodes:
        parent = node.get("visio_group_parent")
        if parent is not None:
            children.setdefault(parent, []).append(node["id"])
    by_id = {node["id"]: node for node in nodes}
    for root_id, delta in shifts.items():
        if delta == 0:
            continue
        pending = [root_id]
        seen = set()
        while pending:
            ident = pending.pop()
            if ident in seen:
                continue
            seen.add(ident)
            by_id[ident][axis] += delta
            pending.extend(children.get(ident, ()))


def align(nodes, identifiers, axis, mode="center"):
    if axis not in ("x", "y"):
        raise ValueError("Unknown alignment axis")
    selected = _selection_roots(nodes, identifiers)
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
    _translate_subtrees(nodes, {node["id"]: target - node[axis] for node in selected}, axis)
    return True


def distribute(nodes, identifiers, axis):
    if axis not in ("x", "y"):
        raise ValueError("Unknown distribution axis")
    selected = sorted(_selection_roots(nodes, identifiers),
                      key=lambda node: (node[axis], node["id"]))
    if len(selected) < 3:
        return False
    first, last = selected[0][axis], selected[-1][axis]
    step = (last - first) / (len(selected) - 1)
    shifts = {node["id"]: first + index * step - node[axis]
              for index, node in enumerate(selected[1:-1], 1)}
    if not any(shifts.values()):
        return False
    _translate_subtrees(nodes, shifts, axis)
    return True


def move_group(nodes, identifiers, dx, dy, spacing=None):
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
