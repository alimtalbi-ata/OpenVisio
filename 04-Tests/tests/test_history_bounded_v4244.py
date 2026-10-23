"""V42.44: dense-diagram history is bounded, reversible, and isolated.
Author: Abdelhalim Talbi.
"""
import unittest
from openvisio.history import History


def dense_document(count=600):
    return {'nodes': [{'id': f'n{i}', 'x': i, 'y': i % 13,
                       'label': 'FC host or array ' + str(i)} for i in range(count)],
            'edges': []}


class BoundedHistoryTests(unittest.TestCase):
    def test_large_snapshots_compressed_and_undo_redo_exact(self):
        original = dense_document()
        h = History(original, compression_threshold=512)
        changed = dense_document()
        changed['nodes'][0]['x'] = 999
        self.assertTrue(h.record(changed))
        self.assertTrue(h.past[0][0], 'large history entry must be compressed')
        self.assertLess(h.history_bytes, 8000)
        original['nodes'][0]['x'] = -1
        undone = h.undo()
        self.assertEqual(undone['nodes'][0]['x'], 0)
        undone['nodes'][0]['x'] = -2
        self.assertEqual(h.redo(), changed)
        self.assertEqual(h.undo()['nodes'][0]['x'], 0)

    def test_budget_eviction_preserves_latest_undo(self):
        h = History(dense_document(200), max_bytes=3500, compression_threshold=0)
        for x in range(10):
            changed = dense_document(200)
            changed['nodes'][0]['x'] = x + 10
            h.record(changed)
        self.assertGreaterEqual(len(h.past), 1)
        self.assertLessEqual(h.history_bytes, 3500)
        self.assertEqual(h.undo()['nodes'][0]['x'], 18)
        self.assertEqual(h.redo()['nodes'][0]['x'], 19)

    def test_redo_cleared_and_reset_rejects_invalid(self):
        h = History(dense_document(20), compression_threshold=0)
        changed = dense_document(20)
        changed['nodes'][0]['x'] = 50
        h.record(changed)
        h.undo()
        with self.assertRaises(ValueError):
            h.reset({'nodes': [], 'edges': [{'id': 'broken', 'from': 'a', 'to': 'b'}]})
        self.assertEqual(h.redo(), changed)
        h.undo()
        changed['nodes'][0]['x'] = 60
        h.record(changed)
        self.assertIsNone(h.redo())

    def test_non_json_extension_retains_legacy_undo(self):
        original = dense_document(2)
        original['nodes'][0]['internal_set'] = {'x', 'y'}
        h = History(original, compression_threshold=0)
        updated = dense_document(2)
        updated['nodes'][0]['internal_set'] = {'z'}
        h.record(updated)
        self.assertEqual(h.undo()['nodes'][0]['internal_set'], {'x', 'y'})
        self.assertEqual(h.redo()['nodes'][0]['internal_set'], {'z'})

    def test_invalid_limits(self):
        for kwargs in ({'limit': 0}, {'max_bytes': 0},
                       {'compression_threshold': -1}, {'limit': True}):
            with self.assertRaises(ValueError):
                History(dense_document(1), **kwargs)


if __name__ == '__main__':
    unittest.main()
