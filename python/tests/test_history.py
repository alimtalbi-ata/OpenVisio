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
        h = History({"n":0})
        h.record({"n":1})
        h.undo()
        h.record({"n":2})
        self.assertIsNone(h.redo())
    def test_invalid_snapshot_is_rejected_without_corrupting_history(self):
        h = History({"nodes": [], "edges": []})
        bad = {"nodes": [{"id": "a", "x": 0, "y": 0}], "edges": [{"id": "e", "from": "a", "to": "missing"}]}
        with self.assertRaises(ValueError):
            h.record(bad)
        self.assertIsNone(h.undo())
        self.assertEqual(h.current, {"nodes": [], "edges": []})

    def test_limit(self):
        h = History({"n":0}, limit=2)
        for i in range(1, 5):
            h.record({"n":i})
        self.assertEqual(h.undo()["n"],3)
        self.assertEqual(h.undo()["n"],2)
        self.assertIsNone(h.undo())
