"""Experimental VSDX interoperability: OPC package, basic geometry, lossless OpenVisio payload.

Supports rectangular infrastructure nodes, unrotated nested group hierarchies,
straight connectors, and static orthogonal connector polylines. Other Visio
features (masters, stencils, text styles, rotated groups, dynamic Visio rerouting, multiple pages) are
not faithfully represented. No Microsoft Visio compatibility claim without an
actual Visio round-trip qualification. Author: Abdelhalim Talbi.
"""
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path
from pathlib import PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from .model import validate, load_bytes, SaveConflict, _sha256
from .save_lock import exclusive_document_lock
from .connector_geometry import connector_endpoints
from .node_geometry import node_bounds, node_dimensions
from .vsdx_polyline import connector_polyline
from .routing import routing_scene
from .parallel_geometry import display_edges
from .connector_labels import edge_label_text
from .vsdx_page_extent import page_extent
from .vsdx_consistency import VISUAL_PARTS, build_manifest, changed_visual_parts

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
PX_PER_IN = 96.0
ET.register_namespace("", V)
ET.register_namespace("r", OR)


def _cell(parent, name, value):
    return ET.SubElement(parent, f"{{{V}}}Cell", {"N": name, "V": str(value)})


def _xml(element):
    return ET.tostring(element, encoding="utf-8", xml_declaration=True)


def _relationships(*items):
    root = ET.Element(f"{{{R}}}Relationships")
    for index, (kind, target) in enumerate(items, 1):
        ET.SubElement(root, f"{{{R}}}Relationship", {
            "Id": f"rId{index}",
            "Type": f"http://schemas.microsoft.com/visio/2010/relationships/{kind}",
            "Target": target,
        })
    return _xml(root)


def _export_vsdx_unlocked(path, document, check_revision, require_absent, *,
                          archive_type=ZipFile, polyline_builder=connector_polyline):
    """Construct and audit a staged VSDX; publish only after rechecking disk."""
    doc = validate(document)
    nodes = doc["nodes"]
    min_x, min_y, width, height, scene = page_extent(nodes, doc["edges"])
    page = ET.Element(f"{{{V}}}PageContents")
    shapes = ET.SubElement(page, f"{{{V}}}Shapes")
    connects = ET.SubElement(page, f"{{{V}}}Connects")
    identifiers = {n["id"]: idx for idx, n in enumerate(nodes, 1)}
    nodes_by_id = {n["id"]: n for n in nodes}
    # Emit actual nested Visio <Shapes> for group descendants.  The previous
    # flat export retained hierarchy only in the private JSON payload: external
    # consumers (including our own flatten importer) lost all grouping.
    # Node positions in OpenVisio are absolute, but Visio child pins are in
    # the coordinate system of the parent group (origin at lower-left).
    children = {None: []}
    for node in nodes:
        children.setdefault(node.get("visio_group_parent"), []).append(node)

    def emit_node(node, destination, parent=None):
        sid = identifiers[node["id"]]
        is_group = node.get("shape") == "visio-group"
        shape = ET.SubElement(destination, f"{{{V}}}Shape", {
            "ID": str(sid), "NameU": "OpenVisio group" if is_group else "OpenVisio node",
            "Name": "OpenVisio group" if is_group else "OpenVisio " + node.get("shape", "server"),
            "Type": "Group" if is_group else "Shape"})
        node_width, node_height = node_dimensions(node)
        if parent is None:
            pin_x = (node["x"] - min_x) / PX_PER_IN
            pin_y = (height - (node["y"] - min_y)) / PX_PER_IN
        else:
            parent_width, parent_height = node_dimensions(parent)
            pin_x = (node["x"] - parent["x"] + parent_width / 2) / PX_PER_IN
            pin_y = (parent["y"] + parent_height / 2 - node["y"]) / PX_PER_IN
        for key, value in (("PinX", pin_x), ("PinY", pin_y),
                           ("Width", node_width / PX_PER_IN),
                           ("Height", node_height / PX_PER_IN),
                           ("LocPinX", node_width / (2 * PX_PER_IN)),
                           ("LocPinY", node_height / (2 * PX_PER_IN))):
            _cell(shape, key, f"{value:.9f}")
        geom = ET.SubElement(shape, f"{{{V}}}Section", {"N": "Geometry", "IX": "0"})
        for index, (kind, x, y) in enumerate((
                ("RelMoveTo", 0, 0), ("RelLineTo", 1, 0),
                ("RelLineTo", 1, 1), ("RelLineTo", 0, 1), ("RelLineTo", 0, 0))):
            row = ET.SubElement(geom, f"{{{V}}}Row", {"T": kind, "IX": str(index)})
            _cell(row, "X", f"{x:.6f}")
            _cell(row, "Y", f"{y:.6f}")
        ET.SubElement(shape, f"{{{V}}}Text").text = node.get("label", node["id"])
        if is_group and children.get(node["id"]):
            nested = ET.SubElement(shape, f"{{{V}}}Shapes")
            for child in children[node["id"]]:
                emit_node(child, nested, node)

    for node in children[None]:
        emit_node(node, shapes)
    for index, edge in enumerate(display_edges(doc["edges"], nodes), len(nodes) + 1):
        a = nodes_by_id[edge["from"]]
        b = nodes_by_id[edge["to"]]
        shape = ET.SubElement(shapes, f"{{{V}}}Shape", {
            "ID": str(index), "NameU": "OpenVisio connector", "Type": "Shape"})
        _cell(shape, "OneD", 1)
        if edge.get("routing") == "orthogonal" or edge.get('_lane_offset'):
            begin, end, rows = polyline_builder(edge, nodes_by_id, min_x, min_y, height, scene=scene)
            for key, point in (("BeginX", begin), ("EndX", end)):
                _cell(shape, key, f"{point[0]:.9f}")
            for key, point in (("BeginY", begin), ("EndY", end)):
                _cell(shape, key, f"{point[1]:.9f}")
            geom = ET.SubElement(shape, f"{{{V}}}Section", {"N": "Geometry", "IX": "0"})
            for idx, (kind, x, y) in enumerate(rows):
                row = ET.SubElement(geom, f"{{{V}}}Row", {"T": kind, "IX": str(idx)})
                _cell(row, "X", f"{x:.9f}")
                _cell(row, "Y", f"{y:.9f}")
        else:
            start, end = connector_endpoints(a, b)
            for key, point in (("BeginX", start), ("EndX", end)):
                _cell(shape, key, f"{(point[0] - min_x)/PX_PER_IN:.6f}")
            for key, point in (("BeginY", start), ("EndY", end)):
                _cell(shape, key, f"{(height - (point[1] - min_y))/PX_PER_IN:.6f}")
            geom = ET.SubElement(shape, f"{{{V}}}Section", {"N": "Geometry", "IX": "0"})
            for idx, (kind, x) in enumerate((("RelMoveTo", 0), ("RelLineTo", 1))):
                row = ET.SubElement(geom, f"{{{V}}}Row", {"T": kind, "IX": str(idx)})
                _cell(row, "X", x)
                _cell(row, "Y", 0)
        # Connector metadata must remain visible to third-party VSDX readers,
        # not only to consumers of the embedded OpenVisio JSON payload.
        public_label = edge_label_text(edge)
        if public_label:
            ET.SubElement(shape, f"{{{V}}}Text").text = public_label
        for cell, target in (("BeginX", identifiers[edge["from"]]),
                             ("EndX", identifiers[edge["to"]])):
            ET.SubElement(connects, f"{{{V}}}Connect", {
                "FromSheet": str(index), "FromCell": cell,
                "ToSheet": str(target), "ToCell": "PinX"})
    pages = ET.Element(f"{{{V}}}Pages")
    pg = ET.SubElement(pages, f"{{{V}}}Page", {"ID": "0", "Name": "Page-1", "NameU": "Page-1"})
    ps = ET.SubElement(pg, f"{{{V}}}PageSheet", {"LineStyle": "0", "FillStyle": "0", "TextStyle": "0"})
    _cell(ps, "PageWidth", f"{width/PX_PER_IN:.6f}")
    _cell(ps, "PageHeight", f"{height/PX_PER_IN:.6f}")
    _cell(ps, "PageScale", 1)
    _cell(ps, "DrawingScale", 1)
    ET.SubElement(pg, f"{{{V}}}Rel", {f"{{{OR}}}id": "rId1"})
    document_xml = ET.Element(f"{{{V}}}VisioDocument")
    ET.SubElement(document_xml, f"{{{V}}}DocumentSettings")
    types = ET.Element(f"{{{CT}}}Types")
    for extension, content_type in (("rels", "application/vnd.openxmlformats-package.relationships+xml"),
                                    ("xml", "application/xml"), ("json", "application/json")):
        ET.SubElement(types, f"{{{CT}}}Default", {"Extension": extension, "ContentType": content_type})
    for part, content_type in (("/visio/document.xml", "application/vnd.ms-visio.drawing.main+xml"),
                               ("/visio/pages/pages.xml", "application/vnd.ms-visio.pages+xml"),
                               ("/visio/pages/page1.xml", "application/vnd.ms-visio.page+xml")):
        ET.SubElement(types, f"{{{CT}}}Override", {"PartName": part, "ContentType": content_type})
    payload = json.dumps(doc, ensure_ascii=False, separators=(",", ":")).encode("utf-8")
    output = Path(path)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd, staging = tempfile.mkstemp(prefix=".openvisio-vsdx-", suffix=".tmp", dir=output.parent)
    os.close(fd)
    try:
        with archive_type(staging, "w", ZIP_DEFLATED) as archive:
            parts = {
                "[Content_Types].xml": _xml(types),
                "_rels/.rels": _relationships(("document", "visio/document.xml")),
                "visio/document.xml": _xml(document_xml),
                "visio/_rels/document.xml.rels": _relationships(("pages", "pages/pages.xml")),
                "visio/pages/pages.xml": _xml(pages),
                "visio/pages/_rels/pages.xml.rels": _relationships(("page", "page1.xml")),
                "visio/pages/page1.xml": _xml(page),
                "openvisio/document.json": payload,
            }
            manifest = build_manifest(parts, payload)
            parts["openvisio/manifest.json"] = json.dumps(
                manifest, ensure_ascii=False, sort_keys=True).encode("utf-8")
            for name, content in parts.items():
                archive.writestr(name, content)
        # Independently parse the *public* Visio page before publishing.
        # A private JSON round-trip alone would conceal broken group/connector XML.
        from .vsdx_fidelity import audit_public_vsdx
        audit_public_vsdx(staging, doc)
        check_revision()
        if require_absent:
            # Atomic no-clobber publication, including a concurrent new file.
            try:
                os.link(staging, output)
            except FileExistsError as exc:
                raise SaveConflict("Le VSDX de destination a été créé pendant l'export") from exc
        else:
            os.replace(staging, output)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)
    return output


