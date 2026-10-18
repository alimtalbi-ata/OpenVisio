import unittest
from openvisio.links import normalize_link
class LinkTests(unittest.TestCase):
    def test_fc(self):
        self.assertEqual(normalize_link(protocol="FC", fabric="A", speed_gbps="32")["speed_gbps"], "32.0")
    def test_iscsi(self):
        self.assertEqual(normalize_link(protocol="iSCSI")["protocol"], "iSCSI")
    def test_invalid_protocol(self):
        with self.assertRaises(ValueError):
            normalize_link(protocol="INVALID")
    def test_invalid_speed(self):
        with self.assertRaises(ValueError):
            normalize_link(speed_gbps="-1")
