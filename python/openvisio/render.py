"""Canvas rendering and geometry, independent from editor state. Author: Abdelhalim Talbi."""
from math import hypot
from .shapes import get_shape
from .routing import routing_scene, RoutingError
from .node_geometry import node_half_sizes
from .connector_geometry import lane_endpoints
from .viewport_visibility import view_window, rect_visible, polyline_visible
from .parallel_geometry import display_edges
from .connector_labels import layout_connector_labels
from .shape_icons import equipment_icon
from .node_labels import label_char_limit, wrap_label_lines

NODE_HALF_WIDTH = 70
NODE_HALF_HEIGHT = 30

def node_at(nodes, x, y, group_border_tolerance=6.0):
    """Hit solid equipment first; Visio groups are transparent outlines.

    Imported groups are drawn with ``fill=""``. Treating their entire
    bounding rectangles as clickable prevented selecting equipment and SAN
    connectors enclosed by a group (especially when the group was last in
    the document). Only the group's visible frame is selectable.
    """
    # Equipment wins over any overlapping transparent group frame.
    for node in reversed(nodes):
        if node.get("shape") == "visio-group":
            continue
        hw, hh = node_half_sizes(node)
        if abs(node["x"] - x) <= hw and abs(node["y"] - y) <= hh:
            return node
    for node in reversed(nodes):
        if node.get("shape") != "visio-group":
            continue
        hw, hh = node_half_sizes(node)
        dx, dy = abs(node["x"] - x), abs(node["y"] - y)
        # Never allow the zoom-adjusted border tolerance to consume the
        # entire group interior at very low zoom.
        border = max(0.0, min(group_border_tolerance, min(hw, hh) / 3))
        if dx <= hw + border and dy <= hh + border and (
            abs(dx - hw) <= border or abs(dy - hh) <= border
        ):
            return node
    return None

def edge_at(nodes, edges, x, y, tolerance=9):
    """Select the *nearest* visible connector within the hit tolerance.

    In dense SAN fabrics, adjacent parallel lanes can be closer than the
    click tolerance. Returning the first matching line made most paths
    impossible to select. On exact ties, preserve reverse draw order (the
    topmost line wins), consistent with historical single-link behavior.
    """
    by_id = {n["id"]: n for n in nodes}
    scene = routing_scene(nodes)
    # Connector captions are drawn above paths and often deliberately offset
    # more than the line's hit tolerance to avoid SAN fabric congestion.
    # Select their actual edge when clicked, not an unrelated nearby lane.
    # Use the same pure layout as Tk/SVG; hidden captions are not clickable.
    captions = layout_connector_labels(nodes, edges, scene=scene).labels
    for edge in reversed(edges):
        label = captions.get(edge["id"])
        if label is not None:
            x0, y0, x1, y1 = label.bounds
            if x0 <= x <= x1 and y0 <= y <= y1:
                return edge
    best_edge = None
    best_distance = float("inf")
    for edge in reversed(display_edges(edges, nodes)):
        a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
        if not a or not b:
            continue
        try:
            points = scene.route_points(edge)
        except RoutingError:
            continue  # Invalid paths are never selectable as valid connectors.
        for (ax, ay), (bx, by) in zip(points, points[1:]):
            dx, dy = bx - ax, by - ay
            length_sq = dx * dx + dy * dy
            if not length_sq:
                continue
            t = max(0, min(1, ((x - ax) * dx + (y - ay) * dy) / length_sq))
            distance = hypot(x - (ax + t * dx), y - (ay + t * dy))
            if distance <= tolerance and distance < best_distance:
                best_edge, best_distance = edge, distance
    return best_edge


def object_at(nodes, edges, x, y, *, node_tolerance=6.0, edge_tolerance=9.0):
    """Select FC links crossing imported transparent Visio group frames.

    Solid equipment has priority; a group frame only wins if no connector
    lies under the pointer. Shared by click and context-menu resolution.
    """
    node = node_at(nodes, x, y, group_border_tolerance=node_tolerance)
    edge = (None if node is not None and node.get("shape") != "visio-group"
            else edge_at(nodes, edges, x, y, tolerance=edge_tolerance))
    return resolve_hit(node, edge)


def resolve_hit(node, edge):
    """Consistent object priority for the editor and pure geometry tests."""
    if node is not None and node.get("shape") != "visio-group":
        return node, None
    if edge is not None:
        return None, edge
    return node, None

def draw_document(canvas, document, selected_node=None, selected_edge=None, viewport=None, grid=False, grid_spacing=20, selected_nodes=None):
    import tkinter as tk
    canvas.delete("all")
    def xy(x, y):
        return viewport.screen(x, y) if viewport is not None else (x, y)
    scale = viewport.zoom if viewport is not None else 1.0
    # Viewport culling is intentionally restricted to Tk drawing. The complete
    # topology remains available to routing, selection, SVG and VSDX export.
    window = (view_window(viewport, canvas.winfo_width(), canvas.winfo_height())
              if viewport is not None else None)
    if grid:
        width, height = canvas.winfo_width(), canvas.winfo_height()
        zoom = viewport.zoom if viewport is not None else 1
        if zoom * grid_spacing >= 8:
            x0, y0 = viewport.world(0, 0) if viewport is not None else (0, 0)
            x1, y1 = viewport.world(width, height) if viewport is not None else (width, height)
            import math
            for i in range(math.floor(x0 / grid_spacing), math.ceil(x1 / grid_spacing) + 1):
                sx = xy(i * grid_spacing, 0)[0]
                canvas.create_line(sx, 0, sx, height, fill="#e2e8f0", tags=(f"ov:grid:v:{i}",))
            for i in range(math.floor(y0 / grid_spacing), math.ceil(y1 / grid_spacing) + 1):
                sy = xy(0, i * grid_spacing)[1]
                canvas.create_line(0, sy, width, sy, fill="#e2e8f0", tags=(f"ov:grid:h:{i}",))
    by_id = {n["id"]: n for n in document["nodes"]}
    scene = routing_scene(document["nodes"])
    label_layout = layout_connector_labels(document["nodes"], document["edges"], scene=scene)
    visible_ids = None
    if window is not None:
        # Scene geometry already owns a cached, exact rectangle index. Reuse it
        # instead of constructing an independent O(N log N) index per redraw.
        visible_ids = ({node_id for node_id, _ in scene.geometry()[3].query_items(window)}
                       if document["nodes"] else set())
    for edge_index, edge in enumerate(display_edges(document["edges"], document["nodes"])):
        a, b = by_id.get(edge["from"]), by_id.get(edge["to"])
        if a and b:
            selected = edge.get("id") == selected_edge
            edge_key = str(edge.get("id", f"unnamed-{edge_index}"))
            # Straight paths are entirely enclosed by their endpoint AABB.
            # This cheap rejection avoids even asking the routing engine for
            # edges that cannot touch the screen. Orthogonal paths MUST still
            # be computed: they can detour into view from offscreen endpoints.
            if window is not None and edge.get("routing", "straight") != "orthogonal":
                endpoints = lane_endpoints(a, b, edge.get('_lane_offset', 0.0))
                if not polyline_visible(endpoints, window):
                    continue
            try:
                points = scene.route_points(edge)
            except RoutingError:
                error_x, error_y = (a["x"] + b["x"]) / 2, (a["y"] + b["y"]) / 2
                if window is None or rect_visible((error_x, error_y, error_x, error_y), window):
                    mx, my = xy(error_x, error_y)
                    canvas.create_text(mx, my, text="⚠ Routage impossible : repositionnez les équipements",
                                       fill="#b91c1c", font=("Arial", max(8, int(10 * scale))),
                                       tags=(f"ov:edge:{edge_key}:error",))
                continue
            if window is not None and not polyline_visible(points, window):
                continue
            coords = [v for point in points for v in xy(*point)]
            canvas.create_line(*coords, fill="#dc2626" if selected else "#2563eb", width=(4 if selected else 2) * scale, arrow=tk.LAST, tags=(f"ov:edge:{edge_key}:path",))
            label = label_layout.labels.get(edge.get("id"))
            if label is not None and (window is None or rect_visible(label.bounds, window)):
                lx, ly = xy(label.x, label.y)
                canvas.create_text(lx, ly, text=label.text,
                                   fill="#991b1b" if selected else "#334155",
                                   font=("Arial", max(6, int(9 * scale))),
                                   tags=(f"ov:edge:{edge_key}:label",))
    for node in document["nodes"]:
        if visible_ids is not None and node["id"] not in visible_ids:
            continue
        x, y = node["x"], node["y"]
        selected = node["id"] == selected_node or node["id"] in (selected_nodes or ())
        hw, hh = node_half_sizes(node)
        is_group = node.get("shape") == "visio-group"
        canvas.create_rectangle(*xy(x-hw, y-hh), *xy(x+hw, y+hh),
                                fill="" if is_group else ("#bfdbfe" if selected else get_shape(node.get("shape", "server"))["fill"]),
                                outline="#64748b" if is_group else "#1d4ed8",
                                dash=(6, 3) if is_group else (),
                                width=(3 if selected else 1) * scale,
                                tags=(f"ov:node:{node['id']}:rect",))
        # A dedicated, stable retained item makes equipment types distinguishable
        # without replacing the node hit box or changing connector attachments.
        icon = equipment_icon(node)
        if icon is not None and hasattr(canvas, "create_polygon"):
            canvas.create_polygon(*(coord for point in icon for coord in xy(*point)),
                                  fill="#f8fafc", outline="#334155", width=max(1, scale),
                                  tags=(f"ov:node:{node['id']}:icon",))
        label_x, label_y = (x - hw + 10, y - hh + 12) if is_group else (x, y)
        font_size = max(6, int(10 * scale))
        inner_padding = 20 if is_group else 12
        logical_limit = label_char_limit(2 * hw, font_size=13, padding=inner_padding)
        pixel_width = max(1.0, (2 * hw - inner_padding) * scale)
        zoom_limit = max(1, int(pixel_width / (font_size * 0.62)))
        visual_label = "\n".join(wrap_label_lines(
            node.get("label", "Équipement"), min(logical_limit, zoom_limit)))
        canvas.create_text(*xy(label_x, label_y), text=visual_label,
                           width=pixel_width, justify="left" if is_group else "center",
                           anchor="w" if is_group else "center",
                           fill="#334155" if is_group else "#172554",
                           font=("Arial", font_size),
                           tags=(f"ov:node:{node['id']}:label",))

    if label_layout.hidden:
        # Never present an omitted metadata label as if it were drawn.
        canvas.create_text(12, 16, anchor="nw",
                           text=f"{len(label_layout.hidden)} étiquette(s) masquée(s) : espace insuffisant",
                           fill="#92400e", font=("Arial", 9),
                           tags=("ov:labels:warning",))
