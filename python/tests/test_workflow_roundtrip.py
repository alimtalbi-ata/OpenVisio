"""End-to-end model workflow without a graphical display. Author: Abdelhalim Talbi."""
import tempfile
import unittest
from pathlib import Path

from openvisio.commands import add_equipment, connect_equipment, remove_selection
from openvisio.history import History
from openvisio.model import load, save
from openvisio.property_commands import update_equipment, update_connection

class WorkflowRoundTripTests(unittest.TestCase):
    def test_create_edit_undo_redo_save_reopen(self):
        original = {"nodes": [], "edges": []}
        history = History(original)
        document, a = add_equipment(original, 100, 200, ident="nas")
        self.assertTrue(history.record(document))
        document, b = add_equipment(document, 300, 200, ident="switch")
        self.assertTrue(history.record(document))
        document = connect_equipment(document, a, b, ident="fc-link")
        self.assertTrue(history.record(document))
        document = update_equipment(document, a, {"label": "NAS-01", "address": "192.0.2.10"}, "server")
        self.assertTrue(history.record(document))
        document = update_connection(document, "fc-link", {"protocol": "FC", "speed_gbps": "32"})
        self.assertTrue(history.record(document))
        expected = document
        self.assertEqual(history.undo()["edges"][0].get("speed_gbps"), None)
        self.assertEqual(history.redo(), expected)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "roundtrip.ovjson"
            save(path, expected)
            self.assertEqual(load(path), expected)

    def test_delete_undo_and_reopen(self):
        document = {"nodes": [], "edges": []}
        document, a = add_equipment(document, 10, 20, ident="a")
        document, b = add_equipment(document, 40, 50, ident="b")
        document = connect_equipment(document, a, b, ident="e")
        history = History(document)
        deleted = remove_selection(document, {a})
        self.assertEqual(deleted["edges"], [])
        self.assertTrue(history.record(deleted))
        self.assertEqual(history.undo(), document)
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "restored.ovjson"
            save(path, history.current)
            self.assertEqual(load(path), document)
