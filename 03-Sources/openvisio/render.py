"""Canvas rendering and geometry, independent from editor state. Author: Abdelhalim Talbi."""
from math import hypot
from .shapes import get_shape
from .symbols import draw_symbol

NODE_HALF_WIDTH = 70
NODE_HALF_HEIGHT = 30

def node_at(nodes, x, y):
    for node in reversed(nodes):
        if abs(node["x"] - x) <= NODE_HALF_WIDTH and abs(node["y"] - y) <= NODE_HALF_HEIGHT:
            return node
    return None


def edge_routes(nodes, edges, spacing=18):
    """Return stable, distinct routes for physical links sharing endpoints."""
    groups = {}
    by_id = {node["id"]: node for node in nodes}
    for edge in edges:
        groups.setdefault(tuple(sorted((edge["from"], edge["to"]))), []).append(edge)
    routes = {}
    for group in groups.values():
        for index, edge in enumerate(group):
            a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
            if a is None or b is None:
                continue
            dx, dy = b["x"] - a["x"], b["y"] - a["y"]
            length = hypot(dx, dy)
            if length == 0:
                continue
            sign = 1 if edge["from"] < edge["to"] else -1
            lane = (index - (len(group) - 1) / 2) * spacing
            ox, oy = -dy / length * lane * sign, dx / length * lane * sign
            routes[edge["id"]] = ((a["x"] + ox, a["y"] + oy), (b["x"] + ox, b["y"] + oy))
    return routes

def clip_route_to_nodes(route, source, target):
    """Attach lane endpoints to equipment rectangles, including wide lanes."""
    (ax, ay), (bx, by) = route
    dx, dy = bx - ax, by - ay
    if dx == 0 and dy == 0:
        return route
    def boundary(cx, cy, px, py, vx, vy):
        rx, ry = px - cx, py - cy
        if abs(rx) <= NODE_HALF_WIDTH and abs(ry) <= NODE_HALF_HEIGHT:
            tx = (NODE_HALF_WIDTH - abs(rx)) / abs(vx) if vx else float("inf")
            ty = (NODE_HALF_HEIGHT - abs(ry)) / abs(vy) if vy else float("inf")
            return (px + vx * max(0, min(tx, ty)), py + vy * max(0, min(tx, ty)))
        return (max(cx-NODE_HALF_WIDTH, min(cx+NODE_HALF_WIDTH, px)),
                max(cy-NODE_HALF_HEIGHT, min(cy+NODE_HALF_HEIGHT, py)))
    return boundary(source["x"],source["y"],ax,ay,dx,dy), boundary(target["x"],target["y"],bx,by,-dx,-dy)

def edge_at(nodes, edges, x, y, tolerance=9):
    by_id = {n["id"]: n for n in nodes}
    routes = edge_routes(nodes, edges)
    for edge in reversed(edges):
        route = routes.get(edge["id"])
        if route is None:
            continue
        (ax, ay), (bx, by) = clip_route_to_nodes(route, by_id[edge["from"]], by_id[edge["to"]])
        dx, dy = bx - ax, by - ay
        length_sq = dx*dx + dy*dy
        if not length_sq:
            continue
        t = max(0, min(1, ((x-ax)*dx+(y-ay)*dy)/length_sq))
        if hypot(x-(ax+t*dx), y-(ay+t*dy)) <= tolerance:
            return edge
    return None

def draw_document(canvas, document, selected_node=None, selected_edge=None, viewport=None, grid=False, grid_spacing=20, selected_nodes=None):
    import tkinter as tk
    canvas.delete("all")
    def xy(x, y):
        return viewport.screen(x, y) if viewport is not None else (x, y)
    scale = viewport.zoom if viewport is not None else 1.0
    if grid:
        width, height = canvas.winfo_width(), canvas.winfo_height()
        zoom = viewport.zoom if viewport is not None else 1
        if zoom * grid_spacing >= 8:
            x0, y0 = viewport.world(0, 0) if viewport is not None else (0, 0)
            x1, y1 = viewport.world(width, height) if viewport is not None else (width, height)
            import math
            for i in range(math.floor(x0 / grid_spacing), math.ceil(x1 / grid_spacing) + 1):
                sx = xy(i * grid_spacing, 0)[0]
                canvas.create_line(sx, 0, sx, height, fill="#e2e8f0")
            for i in range(math.floor(y0 / grid_spacing), math.ceil(y1 / grid_spacing) + 1):
                sy = xy(0, i * grid_spacing)[1]
                canvas.create_line(0, sy, width, sy, fill="#e2e8f0")
    by_id = {n["id"]: n for n in document["nodes"]}
    routes = edge_routes(document["nodes"], document["edges"])
    for edge in document["edges"]:
        route = routes.get(edge["id"])
        if route is not None:
            (ax, ay), (bx, by) = clip_route_to_nodes(route, by_id[edge["from"]], by_id[edge["to"]])
            selected = edge.get("id") == selected_edge
            canvas.create_line(*xy(ax, ay), *xy(bx, by), fill="#dc2626" if selected else "#2563eb", width=(4 if selected else 2) * scale, arrow=tk.LAST)
            details = []
            protocol = str(edge.get("protocol", "")).strip()
            if protocol:
                details.append(protocol)
            speed = str(edge.get("speed_gbps", "")).strip()
            if speed:
                details.append(speed + " Gbit/s")
            fabric = str(edge.get("fabric", "")).strip()
            if fabric:
                details.append("Fabric " + fabric)
            ports = " → ".join(str(edge.get(key, "")).strip() for key in ("source_port", "target_port") if str(edge.get(key, "")).strip())
            if ports:
                details.append(ports)
            if details:
                mx, my = xy((ax + bx) / 2, (ay + by) / 2)
                canvas.create_text(mx, my - 9 * scale, text=" · ".join(details)[:72], fill="#991b1b" if selected else "#334155", font=("Arial", max(6, int(9 * scale))), tags=("edge-label",))
    for node in document["nodes"]:
        x, y = node["x"], node["y"]
        selected = node["id"] == selected_node or node["id"] in (selected_nodes or ())
        draw_symbol(canvas, node.get("shape", "server"), x, y, xy, scale, selected)
        canvas.create_text(*xy(x, y+33), text=node.get("label", "Équipement")[:40], fill="#172554", font=("Arial", max(6, int(10 * scale))))
