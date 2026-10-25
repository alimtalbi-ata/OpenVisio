"""Format-level release document QA guard regressions (standard library only)."""
from __future__ import annotations

import sys
import tempfile
import unittest
import zipfile
from pathlib import Path
from xml.etree import ElementTree

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / "02-Compilation"))
from release_document_guard import audit_document_artifacts  # noqa: E402

W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
CT = "http://schemas.openxmlformats.org/package/2006/content-types"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"


def make_docx(path: Path, text: str) -> None:
    doc = ElementTree.Element(f"{{{W}}}document")
    body = ElementTree.SubElement(doc, f"{{{W}}}body")
    paragraph = ElementTree.SubElement(body, f"{{{W}}}p")
    run = ElementTree.SubElement(paragraph, f"{{{W}}}r")
    text_node = ElementTree.SubElement(run, f"{{{W}}}t")
    text_node.text = text
    types = ElementTree.Element(f"{{{CT}}}Types")
    ElementTree.SubElement(types, f"{{{CT}}}Default", {
        "Extension": "rels",
        "ContentType": "application/vnd.openxmlformats-package.relationships+xml",
    })
    ElementTree.SubElement(types, f"{{{CT}}}Default", {
        "Extension": "xml",
        "ContentType": "application/xml",
    })
    relationships = ElementTree.Element(f"{{{REL}}}Relationships")
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("[Content_Types].xml", ElementTree.tostring(types, encoding="utf-8"))
        archive.writestr("_rels/.rels", ElementTree.tostring(relationships, encoding="utf-8"))
        archive.writestr("word/document.xml", ElementTree.tostring(doc, encoding="utf-8"))


def make_pdf(path: Path, *, signature=True, eof=True) -> None:
    body = (b"%PDF-1.7\n" if signature else b"NOT-PDF\n") + (b"x" * 1400)
    if eof:
        body += b"\n%%EOF\n"
    path.write_bytes(body)


class ReleaseDocumentGuardTests(unittest.TestCase):
    def test_valid_structured_docx_and_rendered_pdf_pass(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docx = root / "brief.docx"
            pdf = root / "brief.pdf"
            make_docx(docx, "OpenVisio V43.21 " + "Verified source, builds and qualification limits. " * 12)
            make_pdf(pdf)
            report = audit_document_artifacts(
                docx, pdf, pdf_pages=2, pdf_visible_characters=1200
            )
        self.assertTrue(report["ok"], report["errors"])
        self.assertEqual(report["docx_status"], "PASS")
        self.assertEqual(report["pdf_status"], "PASS")
        self.assertGreater(report["docx_text_characters"], 300)

    def test_incomplete_docx_package_is_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docx = root / "brief.docx"
            pdf = root / "brief.pdf"
            with zipfile.ZipFile(docx, "w") as archive:
                archive.writestr("word/document.xml", b"<document/>")
            make_pdf(pdf)
            report = audit_document_artifacts(
                docx, pdf, pdf_pages=1, pdf_visible_characters=600
            )
        self.assertFalse(report["ok"])
        self.assertEqual(report["docx_status"], "FAIL")
        self.assertTrue(any("DOCX incomplet" in item for item in report["errors"]))

    def test_short_docx_text_is_rejected_even_when_package_is_valid(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docx = root / "brief.docx"
            pdf = root / "brief.pdf"
            make_docx(docx, "OpenVisio V43.21")
            make_pdf(pdf)
            report = audit_document_artifacts(
                docx, pdf, pdf_pages=1, pdf_visible_characters=600
            )
        self.assertFalse(report["ok"])
        self.assertTrue(any("contenu texte insuffisant" in item for item in report["errors"]))

    def test_invalid_pdf_signature_and_missing_eof_are_rejected(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docx = root / "brief.docx"
            pdf = root / "brief.pdf"
            make_docx(docx, "OpenVisio V43.21 " + "Qualification content. " * 20)
            make_pdf(pdf, signature=False, eof=False)
            report = audit_document_artifacts(
                docx, pdf, pdf_pages=2, pdf_visible_characters=800
            )
        self.assertFalse(report["ok"])
        self.assertEqual(report["pdf_status"], "FAIL")
        self.assertTrue(any("signature invalide" in item for item in report["errors"]))
        self.assertTrue(any("marqueur EOF absent" in item for item in report["errors"]))

    def test_low_page_or_text_counts_fail_closed(self):
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            docx = root / "brief.docx"
            pdf = root / "brief.pdf"
            make_docx(docx, "OpenVisio V43.21 " + "Qualification content. " * 20)
            make_pdf(pdf)
            report = audit_document_artifacts(
                docx, pdf, pdf_pages=0, pdf_visible_characters=10
            )
        self.assertFalse(report["ok"])
        self.assertEqual(report["pdf_status"], "FAIL")


if __name__ == "__main__":
    unittest.main()
