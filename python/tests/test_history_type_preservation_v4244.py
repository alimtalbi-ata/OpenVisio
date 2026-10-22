"""V42.44 regression: undo must preserve non-JSON extension types.
Author: Abdelhalim Talbi.
"""
import unittest
from openvisio.history import History

class HistoryExtensionTypeTests(unittest.TestCase):
    def test_tuple_and_integer_mapping_keys_survive_undo(self):
        original = {"nodes": [{"id": "a", "x": 1, "y": 2,
                    "custom_tuple": (1, 2), "custom_keys": {7: "seven"}}], "edges": []}
        edited = {"nodes": [{"id": "a", "x": 5, "y": 2}], "edges": []}
        history = History(original, compression_threshold=0)
        history.record(edited)
        restored = history.undo()
        self.assertEqual(restored["nodes"][0]["custom_tuple"], (1, 2))
        self.assertEqual(restored["nodes"][0]["custom_keys"], {7: "seven"})
        self.assertEqual(history.redo(), edited)

if __name__ == "__main__":
    unittest.main()
