"""SVG export must never emit malformed geometry or non-finite dimensions.

Synthetic OpenVisio export checks; not a Microsoft Visio Desktop fidelity test.
Author: Abdelhalim Talbi.
"""
import math
import unittest
import xml.etree.ElementTree as ET

from openvisio.export import to_svg


DOCUMENT = {'nodes': [{'id': 'host', 'x': 120, 'y': 90, 'shape': 'server'}], 'edges': []}


class SvgDimensionIntegrityTests(unittest.TestCase):
    def test_explicit_dimensions_preserved(self):
        root = ET.fromstring(to_svg(DOCUMENT, width=640, height=480))
        self.assertEqual(root.attrib['width'], '640')
        self.assertEqual(root.attrib['height'], '480')

    def test_default_dimensions_are_finite_and_positive(self):
        root = ET.fromstring(to_svg(DOCUMENT))
        self.assertTrue(all(math.isfinite(float(x)) for x in root.attrib['viewBox'].split()))
        self.assertGreater(float(root.attrib['width']), 0)
        self.assertGreater(float(root.attrib['height']), 0)

    def test_reject_nonfinite_width(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Dimensions SVG'):
                to_svg(DOCUMENT, width=value)

    def test_reject_nonfinite_height(self):
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Dimensions SVG'):
                to_svg(DOCUMENT, height=value)

    def test_reject_bool_dimensions(self):
        for name in ('width', 'height'):
            for value in (True, False):
                with self.subTest(name=name, value=value), self.assertRaisesRegex(ValueError, 'Dimensions SVG'):
                    to_svg(DOCUMENT, **{name: value})

    def test_reject_invalid_margins(self):
        for value in (math.nan, math.inf, -math.inf, -1, True, '80'):
            with self.subTest(value=value), self.assertRaisesRegex(ValueError, 'Marge SVG'):
                to_svg(DOCUMENT, margin=value)

    def test_zero_margin_supported(self):
        root = ET.fromstring(to_svg(DOCUMENT, margin=0))
        self.assertEqual(float(root.attrib['viewBox'].split()[2]), 140)


if __name__ == '__main__':
    unittest.main()
