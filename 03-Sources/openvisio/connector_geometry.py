"""Shared connector geometry for rectangular OpenVisio nodes."""
from math import isfinite

def connector_endpoints(source, target, half_width=70.0, half_height=30.0):
    ax, ay = float(source["x"]), float(source["y"])
    bx, by = float(target["x"]), float(target["y"])
    if not all(isfinite(v) for v in (ax, ay, bx, by, half_width, half_height)):
        raise ValueError("Invalid connector coordinates")
    if half_width <= 0 or half_height <= 0:
        raise ValueError("Invalid rectangle dimensions")
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return (ax, ay), (bx, by)
    factors = []
    if dx:
        factors.append(half_width / abs(dx))
    if dy:
        factors.append(half_height / abs(dy))
    t = min(factors)
    if t >= 0.5:
        return (ax, ay), (bx, by)
    return (ax + dx * t, ay + dy * t), (bx - dx * t, by - dy * t)
