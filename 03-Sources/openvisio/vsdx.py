"""Experimental VSDX interoperability. Author: Abdelhalim Talbi."""
import hashlib
import json
import math
import os
import tempfile
from pathlib import Path, PurePosixPath
from xml.etree import ElementTree as ET
from zipfile import ZipFile, ZIP_DEFLATED
from .model import validate, load_bytes
from .vsdx_consistency import VISUAL_PARTS, build_manifest, changed_visual_parts
from .vsdx_manifest_schema import validate_manifest_schema

V = "http://schemas.microsoft.com/office/visio/2011/1/core"
R = "http://schemas.openxmlformats.org/package/2006/relationships"
OR = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
PX_PER_IN = 96.0
class VsdxExternalChangesError(ValueError):
    """Embedded OpenVisio data no longer matches Visio drawing pages."""

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
            "Type": ("http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" if kind == "document" else f"http://schemas.microsoft.com/visio/2010/relationships/{kind}"),
            "Target": target,
        })
    return _xml(root)

def export_vsdx(path, document):
    """Export a basic single-page VSDX with embedded validated OpenVisio data."""
    doc = validate(document)
    nodes = doc["nodes"]
    min_x = min((n["x"] for n in nodes), default=0) - 140
    min_y = min((n["y"] for n in nodes), default=0) - 100
    max_x = max((n["x"] for n in nodes), default=800) + 140
    max_y = max((n["y"] for n in nodes), default=600) + 100
    width = max(800, max_x - min_x)
    height = max(600, max_y - min_y)
    page = ET.Element(f"{{{V}}}PageContents")
    shapes = ET.SubElement(page, f"{{{V}}}Shapes")
    connects = ET.SubElement(page, f"{{{V}}}Connects")
    identifiers = {n["id"]: idx for idx, n in enumerate(nodes, 1)}
    nodes_by_id = {n["id"]: n for n in nodes}
    for node in nodes:
        sid = identifiers[node["id"]]
        shape = ET.SubElement(shapes, f"{{{V}}}Shape", {
            "ID": str(sid), "NameU": "OpenVisio node", "Type": "Shape"})
        for key, value in (("PinX", (node["x"] - min_x) / PX_PER_IN),
                           ("PinY", (height - (node["y"] - min_y)) / PX_PER_IN),
                           ("Width", 140 / PX_PER_IN), ("Height", 60 / PX_PER_IN),
                           ("LocPinX", 70 / PX_PER_IN), ("LocPinY", 30 / PX_PER_IN)):
            _cell(shape, key, f"{value:.6f}")
        geom = ET.SubElement(shape, f"{{{V}}}Section", {"N": "Geometry", "IX": "0"})
        for index, (kind, x, y) in enumerate((
            ("RelMoveTo", 0, 0), ("RelLineTo", 1, 0),
            ("RelLineTo", 1, 1), ("RelLineTo", 0, 1), ("RelLineTo", 0, 0))):
            row = ET.SubElement(geom, f"{{{V}}}Row", {"T": kind, "IX": str(index)})
            _cell(row, "X", f"{x:.6f}")
            _cell(row, "Y", f"{y:.6f}")
        ET.SubElement(shape, f"{{{V}}}Text").text = node.get("label", node["id"])
    for index, edge in enumerate(doc["edges"], len(nodes) + 1):
        a = nodes_by_id[edge["from"]]
        b = nodes_by_id[edge["to"]]
        shape = ET.SubElement(shapes, f"{{{V}}}Shape", {
            "ID": str(index), "NameU": "OpenVisio connector", "Type": "Shape"})
        _cell(shape, "OneD", 1)
        for key, node in (("BeginX", a), ("EndX", b)):
            _cell(shape, key, f"{(node['x'] - min_x)/PX_PER_IN:.6f}")
        for key, node in (("BeginY", a), ("EndY", b)):
            _cell(shape, key, f"{(height - (node['y'] - min_y))/PX_PER_IN:.6f}")
        geom = ET.SubElement(shape, f"{{{V}}}Section", {"N": "Geometry", "IX": "0"})
        for idx, (kind, x) in enumerate((("RelMoveTo", 0), ("RelLineTo", 1))):
            row = ET.SubElement(geom, f"{{{V}}}Row", {"T": kind, "IX": str(idx)})
            _cell(row, "X", x)
            _cell(row, "Y", 0)
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
        with ZipFile(staging, "w", ZIP_DEFLATED) as archive:
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
            for name, value in parts.items():
                archive.writestr(name, value)
        os.replace(staging, output)
    finally:
        if os.path.exists(staging):
            os.unlink(staging)
    return output

def import_vsdx(path, *, changed_pages="reject"):
    """Reject edited Visio drawing pages unless explicit partial flattening is requested."""
    if changed_pages not in ("reject", "flatten"):
        raise ValueError("Mode d'import des pages VSDX invalide")
    with ZipFile(path) as archive:
        entries = archive.infolist()
        if len(entries) > 5000 or sum(entry.file_size for entry in entries) > 50_000_000:
            raise ValueError("VSDX trop volumineux")
        if len({entry.filename.replace("\\", "/").casefold() for entry in entries}) != len(entries):
            raise ValueError("Entrées VSDX dupliquées")
        for entry in entries:
            if entry.file_size > 1_000_000 and entry.file_size > max(1, entry.compress_size) * 200:
                raise ValueError("VSDX à compression suspecte")
            name = entry.filename.replace("\\", "/")
            parts = PurePosixPath(name).parts
            if (entry.file_size > 10_000_000 or ".." in parts
                    or name.startswith("/") or "\\" in entry.filename
                    or (parts and ":" in parts[0])):
                raise ValueError("Entrée VSDX non sûre")
        if "openvisio/manifest.json" in archive.namelist() and "openvisio/document.json" not in archive.namelist():
            raise ValueError("Document OpenVisio/VSDX manquant pour le manifeste présent")
        if "openvisio/document.json" in archive.namelist():
            if archive.getinfo("openvisio/document.json").file_size > 10_000_000:
                raise ValueError("Document OpenVisio/VSDX trop volumineux")
            if archive.getinfo("openvisio/manifest.json").file_size > 1_000_000:
                raise ValueError("Manifeste OpenVisio/VSDX trop volumineux")
            payload = archive.read("openvisio/document.json")
            if "openvisio/manifest.json" not in archive.namelist():
                raise ValueError("Manifeste OpenVisio/VSDX manquant")
            manifest = json.loads(archive.read("openvisio/manifest.json"))
            if not isinstance(manifest, dict):
                raise ValueError("Manifeste OpenVisio/VSDX invalide : objet JSON attendu")
            schema = validate_manifest_schema(manifest)
            if manifest.get("sha256") != hashlib.sha256(payload).hexdigest():
                raise ValueError("Intégrité OpenVisio/VSDX invalide")
            if schema == 2:
                changed = changed_visual_parts(archive, manifest)
                if changed:
                    if changed_pages == "reject":
                        raise VsdxExternalChangesError(
                            "Pages VSDX modifiées depuis l'export OpenVisio : "
                            + ", ".join(changed)
                            + ". L'import du modèle embarqué ignorerait ces changements. "
                              "Choisissez explicitement l'import géométrique partiel.")
                    from .vsdx_external import import_external_pages
                    imported = import_external_pages(archive)
                    imported.setdefault("metadata", {}).update({
                        "embedded_payload_discarded": True,
                        "changed_parts": changed,
                        "import_warning": "Pages modifiées : import géométrique partiel, "
                                          "sans conservation intégrale des propriétés OpenVisio.",
                    })
                    return validate(imported)
            return load_bytes(payload)
        if not any(name.startswith("visio/pages/") and name.endswith(".xml") and "/_rels/" not in name for name in archive.namelist()):
            raise ValueError("Archive sans page Visio : fichier VSDX invalide")
        from .vsdx_external import import_external_pages
        return import_external_pages(archive)
