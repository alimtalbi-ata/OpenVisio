import unittest
from openvisio.clipboard import copy_selection, paste_selection
from openvisio.model import validate

class ClipboardTests(unittest.TestCase):
    def test_copy_paste_topology_and_ids(self):
        d={"nodes":[{"id":"a","x":0,"y":0},{"id":"b","x":100,"y":100},{"id":"c","x":300,"y":0}],"edges":[{"id":"ab","from":"a","to":"b"},{"id":"bc","from":"b","to":"c"}]}
        payload=copy_selection(d, {"a","b"})
        self.assertEqual(len(payload["edges"]),1)
        ids=paste_selection(d,payload,offset=40)
        self.assertEqual(len(ids),2)
        self.assertEqual(len(d["nodes"]),5)
        self.assertEqual(len(d["edges"]),3)
        self.assertEqual(d["nodes"][3]["x"],40)
        self.assertEqual(d["nodes"][4]["y"],140)
        self.assertTrue(validate(d))
    def test_empty_selection(self):
        d={"nodes":[],"edges":[]}
        self.assertEqual(paste_selection(d,copy_selection(d,set())),set())
