"""Grid, alignment and distribution for infrastructure diagrams.

Native Visio-style groups are positioned in absolute document coordinates:
translating a group envelope must translate all descendants by the same
amount. Author: Abdelhalim Talbi.
"""


def snap(value, spacing=20):
    if spacing <= 0:
        raise ValueError("Grid spacing must be positive")
    return round(value / spacing) * spacing


def _selection_roots(nodes, identifiers):
    """Selected objects, excluding children of another selected ancestor.

    A selected parent owns the movement of its descendants. If both parent and
    child are selected, the child is translated exactly once, and it is not
    counted as an independent alignment/distribution anchor.
    """
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
    """Apply independent root deltas to descendants without double-moving."""
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
    """Evenly distribute >=3 independent objects, preserving nested groups."""
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
    """Translate selected shapes and complete nested groups as one operation.

    Callers may supply only a group envelope or a selection already expanded
    with descendants. In both cases each descendant moves exactly once.
    Snapping uses the first independent selection root as the common anchor;
    all relative positions and connector endpoint IDs remain unchanged.
    """
    roots = _selection_roots(nodes, identifiers)
    if not roots or (dx == 0 and dy == 0):
        return False
    if spacing is not None:
        anchor = roots[0]
        dx = snap(anchor["x"] + dx, spacing) - anchor["x"]
        dy = snap(anchor["y"] + dy, spacing) - anchor["y"]
    if dx == 0 and dy == 0:
        return False
    shifts_x = {node["id"]: dx for node in roots}
    shifts_y = {node["id"]: dy for node in roots}
    _translate_subtrees(nodes, shifts_x, "x")
    _translate_subtrees(nodes, shifts_y, "y")
    return True
