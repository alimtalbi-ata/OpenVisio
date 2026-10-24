"""SVG dimensions must be finite and positive."""
import math
import unittest
from openvisio.export import to_svg

class SvgDimensionsTests(unittest.TestCase):
    def test_nonfinite_dimensions_rejected(self):
        document = {"nodes": [], "edges": []}
        for value in (math.nan, math.inf, -math.inf):
            with self.subTest(value=value):
                with self.assertRaisesRegex(ValueError, "Dimensions SVG"):
                    to_svg(document, width=value)
                with self.assertRaisesRegex(ValueError, "Dimensions SVG"):
                    to_svg(document, height=value)

    def test_valid_dimensions(self):
        result = to_svg({"nodes": [], "edges": []}, width=1024, height=768)
        self.assertIn('width="1024"', result)
        self.assertIn('height="768"', result)
