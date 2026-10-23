import unittest
from openvisio.history import History

class HistoryTests(unittest.TestCase):
    def test_undo_redo(self):
        h = History({"nodes":[],"edges":[]})
        doc = {"nodes":[{"id":"a","x":0,"y":0}],"edges":[]}
        self.assertTrue(h.record(doc))
        doc["nodes"][0]["x"] = 10
        self.assertEqual(h.undo()["nodes"], [])
        self.assertEqual(h.redo()["nodes"][0]["x"], 0)
    def test_new_edit_clears_redo(self):
        h = History({"nodes": [], "edges": []})
        h.record({"nodes": [{"id": "a", "x": 1, "y": 0}], "edges": []})
        h.undo()
        h.record({"nodes": [{"id": "b", "x": 2, "y": 0}], "edges": []})
        self.assertIsNone(h.redo())
    def test_invalid_snapshot_is_rejected_without_corrupting_history(self):
        h = History({"nodes": [], "edges": []})
        bad = {"nodes": [{"id": "a", "x": 0, "y": 0}], "edges": [{"id": "e", "from": "a", "to": "missing"}]}
        with self.assertRaises(ValueError):
            h.record(bad)
        self.assertIsNone(h.undo())
        self.assertEqual(h.current, {"nodes": [], "edges": []})

    def test_reset_rejects_invalid_document_without_erasing_history(self):
        h = History({"nodes": [], "edges": []})
        h.record({"nodes": [{"id": "a", "x": 1, "y": 2}], "edges": []})
        with self.assertRaises(ValueError):
            h.reset({"nodes": [], "edges": [{"id": "orphan", "from": "x", "to": "y"}]})
        self.assertEqual(h.current["nodes"][0]["id"], "a")

    def test_limit(self):
        h = History({"nodes": [], "edges": []}, limit=2)
        for i in range(1, 5):
            h.record({"nodes": [{"id": "a", "x": i, "y": 0}], "edges": []})
        self.assertEqual(h.undo()["nodes"][0]["x"], 3)
        self.assertEqual(h.undo()["nodes"][0]["x"], 2)
        self.assertIsNone(h.undo())
