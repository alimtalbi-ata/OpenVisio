"""Conservative, multi-page import of external Visio VSDX page geometry.

This is a flattening importer, not a Visio fidelity certification. Every Visio
page is mapped to a named OpenVisio layer and vertically offset to avoid overlap.
Masters, exact rotations and style formulas are not
recreated; numeric nested group transforms are flattened to bounding boxes. Author: Abdelhalim Talbi.
"""
import math
import posixpath
import re
from xml.etree import ElementTree as ET
from xml.parsers import expat
from .vsdx_geometry import (shape_center_inches, shape_axis_aligned_dimensions_inches,
                            nested_shape_geometry_inches)

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
PX_PER_IN = 96.0


def _parse_xml(archive, name):
    payload = archive.read(name)
    # A raw-byte <!DOCTYPE check is insufficient: UTF-16 Visio XML can
    # encode every ASCII character with a NUL byte. ElementTree would then
    # expand internal entities before the importer validates the page.
    # Expat recognizes the XML declaration/encoding and rejects any DTD at
    # the parser level, independently of UTF-8/UTF-16 byte representation.
    # Run the preflight before constructing an ElementTree from untrusted XML.
    parser = expat.ParserCreate()

    def reject_dtd(*_args):
        raise ValueError("XML VSDX avec entités externes interdit")

    parser.StartDoctypeDeclHandler = reject_dtd
    parser.EntityDeclHandler = reject_dtd
    parser.ExternalEntityRefHandler = reject_dtd
    try:
        parser.Parse(payload, True)
        return ET.fromstring(payload)
    except (expat.ExpatError, ET.ParseError) as exc:
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
        seen_relation_ids = set()
        for rel in relroot.findall(f"{{{R}}}Relationship"):
            rid = rel.get("Id")
            # OPC relationship IDs are unique within a .rels part. Silently
            # overwriting one changes which Visio page a layer imports.
            if rid:
                if rid in seen_relation_ids:
                    raise ValueError("Identifiant de relation VSDX dupliqué : " + rid)
                seen_relation_ids.add(rid)
            if rel.get("TargetMode", "Internal").lower() == "external":
                continue
            if rid:
                relations[rid] = _part_target(rel.get("Target"))
    result = []
    seen_page_ids = set()
    for i, page in enumerate(pages.findall(f"{{{V}}}Page"), 1):
        page_id = page.get("ID")
        if page_id:
            if page_id in seen_page_ids:
                raise ValueError("Identifiant de page VSDX dupliqué : " + page_id)
            seen_page_ids.add(page_id)
        rel = page.find(f"{{{V}}}Rel")
        rid = rel.get(f"{{{OR}}}id") if rel is not None else None
        part = relations.get(rid)
        # Legacy sequential fallback is valid only when the page does not
        # declare an OPC relationship. A missing/empty/external .rels entry
        # must never silently redirect a named page to page{i}.xml.
        if part is None and not relations and rel is None:
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
    # External Visio NameU values are not OpenVisio catalogue IDs. Preserve
    # explicitly named FC/SAN fabric equipment instead of treating every
    # occurrence of "switch" as a LAN switch. Require adjacent SAN tokens so
    # location names such as "San Francisco Switch" are not misclassified.
    if (re.search(r"\b(?:san[\s_-]*(?:switch|fabric|director)|"
                  r"(?:switch|fabric|director)[\s_-]*san)\b", n)
            or re.search(r"\bfc[\s_-]*(?:switch|fabric|director)\b", n)
            or (re.search(r"\b(?:fibre|fiber)[\s_-]+channel\b", n)
                and re.search(r"\b(?:switch|fabric|director)\b", n))):
        return "san-switch"
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
    page_extent_expanded = 0
    page_bottom_overflow_total = 0.0
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
        top_extent = max((candidate[3] + candidate[7] / 2
                          for candidate in candidates), default=0)
        bottom_extent = min((candidate[3] - candidate[7] / 2
                             for candidate in candidates), default=0)
        # Visio Y increases upwards. Shapes below the page's zero line map
        # below the OpenVisio display band, so the NEXT page needs additional
        # clearance; growing only the current band's height cannot fix this.
        bottom_overflow = max(0.0, -bottom_extent)
        page_bottom_overflow_total += bottom_overflow
        inferred_height = top_extent + 96
        # Preserve coordinates on valid pages. Expand the band above the
        # page only for actual top overflow; reserve bottom overflow in the
        # following page offset without shifting the current page's shapes.
        if declared_height is not None and top_extent <= declared_height:
            height = max(600.0, declared_height)
        else:
            height = max(600.0, inferred_height, declared_height or 0.0)
        if (declared_height is not None and top_extent > declared_height) or bottom_overflow:
            page_extent_expanded += 1
        for ident, sid, x, pin_y, label, kind, width, shape_height, parent_id in candidates:
            node = {"id": ident, "x": round(x, 3),
                    "y": round(offset + height - pin_y, 3),
                    "width": round(width, 3), "height": round(shape_height, 3),
                    "label": label, "shape": kind, "layer": layer_id}
            if parent_id is not None:
                node["visio_group_parent"] = parent_id
            nodes.append(node)
        # Visio connectors are separate Shape elements. Their public Text
        # must survive a source-free import, including formatted Text runs.
        # The label is a caption, not evidence of physical FC port metadata.
        connector_captions = {}
        # Visio connectors can be nested inside group Shapes. The Connects
        # relationship table still references their page-global sheet IDs;
        # searching only top-level shapes silently loses their SAN captions.
        for connector in page.findall(f".//{{{V}}}Shape"):
            sid = connector.get("ID")
            text_element = connector.find(f"./{{{V}}}Text")
            if sid and text_element is not None:
                caption = "".join(text_element.itertext()).strip()
                if caption:
                    connector_captions[sid] = caption[:4096]
        # Only an existing connector sheet may originate a SAN link. A
        # malformed Connects table can otherwise fabricate an edge from a
        # device sheet or an ID that does not exist in the page at all.
        # Nested group connectors are included in this inventory.
        page_shapes = page.findall(f".//{{{V}}}Shape")
        page_sheet_ids = {shape.get("ID") for shape in page_shapes if shape.get("ID")}
        # Visio Connects references a sheet ID, not an individual XML element.
        # If two connector shapes share that ID, their captions and physical
        # SAN links collapse into one ambiguous edge. Reject only duplicate
        # IDs used as connector sources; legacy duplicate non-connector group
        # children are still handled by the existing omission policy.
        connector_sources = {
            row.get("FromSheet")
            for row in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect")
            if row.get("FromCell") in ("BeginX", "EndX") and row.get("FromSheet")
        }
        seen_connector_sources = set()
        for shape in page_shapes:
            sid = shape.get("ID")
            if sid in connector_sources:
                if sid in seen_connector_sources:
                    raise ValueError("Identifiant de connecteur VSDX dupliqué : " + sid)
                seen_connector_sources.add(sid)
        connections = {}
        for link in page.findall(f".//{{{V}}}Connects/{{{V}}}Connect"):
            source, target = link.get("FromSheet"), link.get("ToSheet")
            if source in connector_sources and target not in page_sheet_ids:
                # Do not silently drop a SAN fabric endpoint pointing at a
                # nonexistent Visio sheet. Existing but unsupported grouped
                # children still follow the conservative omission policy.
                raise ValueError(
                    "Connexion VSDX invalide : extrémité SAN absente "
                    f"({source} -> {target})")
            if source and target in by_sheet and link.get("FromCell") in ("BeginX", "EndX"):
                if source in by_sheet or source not in page_sheet_ids:
                    raise ValueError(
                        "Connexion VSDX invalide : feuille de connecteur absente "
                        f"ou équipement utilisé comme connecteur ({source})")
                # A connector end may appear more than once in external Visio
                # Connects tables. Identical rows are harmless, but competing
                # targets would silently change the SAN topology depending on
                # XML ordering. Never invent a winner for an ambiguous link.
                end = link.get("FromCell")
                destination = by_sheet[target]
                previous = connections.setdefault(source, {}).get(end)
                if previous is not None and previous != destination:
                    raise ValueError(
                        "Connexion VSDX ambiguë : extrémité de connecteur "
                        f"{source}/{end} reliée à plusieurs équipements")
                connections[source][end] = destination
        for sid, ends in connections.items():
            a, b = ends.get("BeginX"), ends.get("EndX")
            if a and b and a != b:
                # Distinct Visio connector sheets represent distinct links,
                # even when both terminate on the same pair of devices.
                # Never invent FC port numbers during a geometric import.
                edge = {"id": f"visio-p{index}-link-{sid}",
                        "from": a, "to": b, "layer": layer_id,
                        "visio_connector_sheet_id": str(sid)}
                if sid in connector_captions:
                    edge["label"] = connector_captions[sid]
                edges.append(edge)
        offset += max(height, 600) + 96 + bottom_overflow
    metadata = {"import_format": "VSDX", "page_count": len(pages),
                "import_mode": "flattened-pages",
                "limitations": ["masters", "group-rotation", "rotation", "styles", "formulas"],
                "rotated_shapes_as_bounding_boxes": rotated_count,
                "group_children_omitted": grouped_children_omitted,
                "group_children_imported": grouped_children_imported,
                "page_extent_expanded": page_extent_expanded,
                "page_bottom_overflow_px_total": round(page_bottom_overflow_total, 3)}
    if rotated_count or grouped_children_omitted or grouped_children_imported or page_extent_expanded:
        metadata["fidelity_warnings"] = (
            [f"{rotated_count} rotated Visio shape(s) approximated by axis-aligned bounding boxes"]
            if rotated_count else []) + (
            [f"{grouped_children_omitted} nested group child shape(s) omitted: local transforms unsupported"]
            if grouped_children_omitted else []) + (
            [f"{grouped_children_imported} nested group child shape(s) imported with hierarchy; exact group transforms/rotation not preserved"]
            if grouped_children_imported else []) + (
            [f"{page_extent_expanded} Visio page(s) expanded to contain out-of-page shapes; page layout is approximate"]
            if page_extent_expanded else [])
    return validate({"nodes": nodes, "edges": edges, "layers": layers, "metadata": metadata})
