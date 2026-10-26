"""Structural validation for generated OpenVisio release documents.

The PDF is rendered and text-inspected by generate_release_docs_v4325.py before
this guard runs. This module adds format-level DOCX validation and checks PDF
signature/EOF and observed page/text counts. It deliberately avoids arbitrary
minimum file-size assumptions. Author: Abdelhalim Talbi.
"""
from __future__ import annotations

from pathlib import Path
import zipfile
from xml.etree import ElementTree


def audit_document_artifacts(
    docx_path: Path,
    pdf_path: Path,
    *,
    pdf_pages: int,
    pdf_visible_characters: int,
) -> dict:
    """Validate document structure/content and the already-rendered PDF artifact."""
    errors: list[str] = []
    docx_ok = True
    pdf_ok = True
    docx_bytes = 0
    pdf_bytes = 0
    docx_text_characters = 0

    if not docx_path.is_file():
        docx_ok = False
        errors.append("DOCX absent")
    else:
        docx_bytes = docx_path.stat().st_size
        if docx_bytes <= 0:
            docx_ok = False
            errors.append("DOCX vide")
        else:
            try:
                with zipfile.ZipFile(docx_path, "r") as archive:
                    names = set(archive.namelist())
                    required = {"[Content_Types].xml", "_rels/.rels", "word/document.xml"}
                    missing = sorted(required - names)
                    if missing:
                        docx_ok = False
                        errors.append("DOCX incomplet: " + ", ".join(missing))
                    else:
                        root = ElementTree.fromstring(archive.read("word/document.xml"))
                        text = "".join(
                            node.text or ""
                            for node in root.iter()
                            if node.tag.rsplit("}", 1)[-1] == "t"
                        )
                        docx_text_characters = len(text)
                        if "OpenVisio V43.25" not in text:
                            docx_ok = False
                            errors.append("DOCX: titre de version absent")
                        if len(text.strip()) < 300:
                            docx_ok = False
                            errors.append("DOCX: contenu texte insuffisant")
            except (OSError, KeyError, zipfile.BadZipFile, ElementTree.ParseError) as exc:
                docx_ok = False
                errors.append(f"DOCX illisible: {exc}")

    if not pdf_path.is_file():
        pdf_ok = False
        errors.append("PDF absent")
    else:
        pdf_bytes = pdf_path.stat().st_size
        if pdf_bytes <= 0:
            pdf_ok = False
            errors.append("PDF vide")
        else:
            try:
                with pdf_path.open("rb") as stream:
                    header = stream.read(8)
                    stream.seek(max(0, pdf_bytes - 4096))
                    trailer = stream.read(4096)
                if not header.startswith(b"%PDF-"):
                    pdf_ok = False
                    errors.append("PDF: signature invalide")
                if b"%%EOF" not in trailer:
                    pdf_ok = False
                    errors.append("PDF: marqueur EOF absent")
            except OSError as exc:
                pdf_ok = False
                errors.append(f"PDF illisible: {exc}")

    if not isinstance(pdf_pages, int) or pdf_pages < 1:
        pdf_ok = False
        errors.append("PDF: aucune page validée")
    if not isinstance(pdf_visible_characters, int) or pdf_visible_characters < 500:
        pdf_ok = False
        errors.append("PDF: texte visible insuffisant")

    return {
        "ok": docx_ok and pdf_ok,
        "docx_status": "PASS" if docx_ok else "FAIL",
        "pdf_status": "PASS" if pdf_ok else "FAIL",
        "docx_bytes": docx_bytes,
        "pdf_bytes": pdf_bytes,
        "docx_text_characters": docx_text_characters,
        "pdf_pages": pdf_pages,
        "pdf_visible_characters": pdf_visible_characters,
        "errors": errors,
    }
