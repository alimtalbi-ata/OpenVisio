"""Conservative, multi-page import of external Visio VSDX page geometry.

This is a flattening importer, not a Visio fidelity certification. Every Visio
page is mapped to a named OpenVisio layer and vertically offset to avoid overlap.
Masters, exact rotations and style formulas are not
recreated; numeric nested group transforms are flattened to bounding boxes. Author: Abdelhalim Talbi.
"""
import math
import posixpath
from xml.etree import ElementTree as ET
from .vsdx_geometry import (shape_center_inches, shape_axis_aligned_dimensions_inches,
                            nested_shape_geometry_inches)

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
PX_PER_IN = 96.0


def _parse_xml(archive, name):
    payload = archive.read(name)
    upper = payload.upper()
    if b"<!DOCTYPE" in upper or b"<!ENTITY" in upper:
        raise ValueError("XML VSDX avec entités externes interdit")
    try:
        return ET.fromstring(payload)
    except ET.ParseError as exc:
        raise ValueError("XML VSDX invalide : " + name) from exc


def _part_target(target):
    if not target or "\\" in target or "?" in target or "#" in target:
        raise ValueError("Relation de page VSDX non sûre")
    if target.startswith("/"):
        path = posixpath.normpath(target.lstrip("/"))
    else:
        path = posixpath.normpath(posixpath.join("visio/pages", target))
    if not path.startswith("visio/pages/") or "/../" in "/" + path + "/":
        raise ValueError("Relation de page VSDX non sûre")
    return path


def _pages(archive):
    names = set(archive.namelist())
    pages_xml = "visio/pages/pages.xml"
    rels_xml = "visio/pages/_rels/pages.xml.rels"
    if pages_xml not in names:
        if "visio/pages/page1.xml" not in names:
            raise ValueError("Page Visio absente")
        return [("Page 1", "visio/pages/page1.xml", None)]
    pages = _parse_xml(archive, pages_xml)
    relations = {}
    if rels_xml in names:
        relroot = _parse_xml(archive, rels_xml)
        for rel in relroot.findall(f"{{{R}}}Relationship"):
            if rel.get("TargetMode", "Internal").lower() == "external":
                continue
            if rel.get("Id"):
                relations[rel.get("Id")] = _part_target(rel.get("Target"))
    result = []
    for i, page in enumerate(pages.findall(f"{{{V}}}Page"), 1):
        rel = page.find(f"{{{V}}}Rel")
        rid = rel.get(f"{{{OR}}}id") if rel is not None else None
        part = relations.get(rid)
        if part is None and not relations:
            part = f"visio/pages/page{i}.xml"
        if not part or part not in names:
            raise ValueError("Relation de page VSDX absente ou invalide")
        height = None
        for cell in page.findall(f"./{{{V}}}PageSheet/{{{V}}}Cell"):
            if cell.get("N") == "PageHeight":
                try:
                    value = float(cell.get("V", ""))
                    if math.isfinite(value) and 0 < value <= 100000:
                        height = value * PX_PER_IN
                except ValueError:
                    pass
        result.append((page.get("Name") or page.get("NameU") or f"Page {i}", part, height))
    if not result or len(result) > 128:
        raise ValueError("Nombre de pages VSDX invalide")
    return result


def _kind(name):
    # Recognize our exported infrastructure catalogue without relying on the
    # private OpenVisio JSON payload. Preserve SAN vs network switch types.
    if name.startswith("OpenVisio "):
        from .shapes import SHAPES
        kind = name[len("OpenVisio "):]
        if kind in SHAPES:
            return kind
    n = name.lower()
    if "storage" in n or "array" in n or "disk" in n:
        return "storage"
    if "nas" in n or "fileserver" in n:
        return "nas"
    if "firewall" in n:
        return "firewall"
    if "switch" in n or "router" in n:
        return "network-switch"
    if "database" in n or "sql" in n:
        return "database"
    if "application" in n:
        return "application"
    return "server"


def import_external_pages(archive):
    """Return validated OpenVisio diagram; pages become separate visible layers."""
    from .model import validate

    pages = _pages(archive)
    nodes, edges, layers = [], [], []
    offset = 0.0
    rotated_count = 0
    grouped_children_omitted = 0
    grouped_children_imported = 0
    MAX_GROUP_DEPTH = 16
    for index, (page_name, part, declared_height) in enumerate(pages, 1):
        page = _parse_xml(archive, part)
        layer_id = f"vsdx-page-{index}"
        layers.append({"id": layer_id, "name": page_name[:256], "visible": True})
        candidates = []
        by_sheet = {}
        # Walk nested groups with explicit local-to-page transforms. Keep
        # parent containers as nodes for compatibility with V42.26; children
        # are flattened with their original page-global sheet identifiers.
        # A malformed parent must never cause a guessed child position.
        def descendants_count(shape):
            return len(shape.findall(f".//{{{V}}}Shapes/{{{V}}}Shape"))

        def visit(shape, ancestors=(), parent_id=None, depth=0):
            nonlocal rotated_count, grouped_children_omitted, grouped_children_imported
            children = shape.findall(f"./{{{V}}}Shapes/{{{V}}}Shape")
            sid = shape.get("ID")
            cells = {c.get("N"): c.get("V") for c in shape.findall(f"./{{{V}}}Cell")}
            if depth > MAX_GROUP_DEPTH:
                grouped_children_omitted += 1 + descendants_count(shape)
                return
            if not sid or sid in by_sheet or cells.get("OneD") == "1" or not all(
                    key in cells for key in ("PinX", "PinY")):
                grouped_children_omitted += descendants_count(shape) + (1 if parent_id is not None else 0)
                return
            try:
                x_in, y_in, width_in, height_in, total_angle = nested_shape_geometry_inches(
                    cells, ancestors)
            except ValueError:
                grouped_children_omitted += descendants_count(shape) + (1 if parent_id is not None else 0)
                return
            if not math.isclose(math.remainder(total_angle, math.tau), 0.0, abs_tol=1e-10):
                rotated_count += 1
            ident = f"visio-p{index}-s{sid}"
            name = shape.get("NameU") or shape.get("Name") or ident
            # OpenVisio keeps the stable NameU="OpenVisio node" for older
            # consumers, while the public Name encodes the infrastructure kind.
            if name == "OpenVisio node" and (shape.get("Name") or "").startswith("OpenVisio "):
                name = shape.get("Name")
            text_element = shape.find(f"./{{{V}}}Text")
            label = "".join(text_element.itertext()).strip() if text_element is not None else ""
            candidates.append((ident, sid, x_in * PX_PER_IN, y_in * PX_PER_IN,
                               (label or name)[:4096], "visio-group" if children or shape.get("Type") == "Group" else _kind(name),
                               width_in * PX_PER_IN, height_in * PX_PER_IN, parent_id))
            by_sheet[sid] = ident
            if parent_id is not None:
                grouped_children_imported += 1
            if children:
                # Child geometry cannot be placed without the parent group's
                # explicit Width/Height and valid local pivot/rotation.
                try:
                    from .vsdx_geometry import group_local_to_parent_inches
                    group_local_to_parent_inches(cells, 0.0, 0.0)
                except ValueError:
                    grouped_children_omitted += descendants_count(shape)
                    return
                for child in children:
                    visit(child, ancestors + (cells,), ident, depth + 1)

        for shape in page.findall(f"./{{{V}}}Shapes/{{{V}}}Shape"):
            visit(shape)
        inferred_height = max((candidate[3] + candidate[7] / 2
                               for candidate in candidates), default=0) + 96
        height = declared_height if declared_height is not None else max(600, inferred_height)
        for ident, sid, x, pin_y, label, kind, width, shape_height, parent_id in candidates:
            node = {"id": ident, "x": round(x, 3),
                    "y": round(offset + height - pin_y, 3),
                    "width": round(width, 3), "height": round(shape_height, 3),
                    "label": label, "shape": kind, "layer": layer_id}
            if parent_id is not None:
                node["visio_group_parent"] = parent_id
            nodes.append(node)
        connections = {}
        for link in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect"):
            source, target = link.get("FromSheet"), link.get("ToSheet")
            if source and target in by_sheet and link.get("FromCell") in ("BeginX", "EndX"):
                connections.setdefault(source, {})[link.get("FromCell")] = by_sheet[target]
        for sid, ends in connections.items():
            a, b = ends.get("BeginX"), ends.get("EndX")
            if a and b and a != b:
                # Distinct Visio connector sheets represent distinct links,
                # even when both terminate on the same pair of devices.
                # Never invent FC port numbers during a geometric import.
                edges.append({"id": f"visio-p{index}-link-{sid}",
                              "from": a, "to": b, "layer": layer_id,
                              "visio_connector_sheet_id": str(sid)})
        offset += max(height, 600) + 96
    metadata = {"import_format": "VSDX", "page_count": len(pages),
                "import_mode": "flattened-pages",
                "limitations": ["masters", "group-rotation", "rotation", "styles", "formulas"],
                "rotated_shapes_as_bounding_boxes": rotated_count,
                "group_children_omitted": grouped_children_omitted,
                "group_children_imported": grouped_children_imported}
    if rotated_count or grouped_children_omitted or grouped_children_imported:
        metadata["fidelity_warnings"] = (
            [f"{rotated_count} rotated Visio shape(s) approximated by axis-aligned bounding boxes"]
            if rotated_count else []) + (
            [f"{grouped_children_omitted} nested group child shape(s) omitted: local transforms unsupported"]
            if grouped_children_omitted else []) + (
            [f"{grouped_children_imported} nested group child shape(s) imported with hierarchy; exact group transforms/rotation not preserved"]
            if grouped_children_imported else [])
    return validate({"nodes": nodes, "edges": edges, "layers": layers, "metadata": metadata})
