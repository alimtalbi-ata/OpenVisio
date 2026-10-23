import unittest
from openvisio.properties import normalize_properties

class PropertiesTests(unittest.TestCase):
    def test_valid_ipv4(self):
        self.assertEqual(normalize_properties(" NAS ", address="192.0.2.10", vendor="NetApp")["label"], "NAS")
    def test_valid_ipv6(self):
        self.assertEqual(normalize_properties("Switch", address="2001:db8::1")["address"], "2001:db8::1")
    def test_invalid_ip(self):
        with self.assertRaises(ValueError):
            normalize_properties("NAS", address="invalid ip")
    def test_empty_label(self):
        with self.assertRaises(ValueError):
            normalize_properties("  ")
