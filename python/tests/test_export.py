import unittest
from openvisio.export import to_svg

class SvgTests(unittest.TestCase):
    def test_escaped_label(self):
        xml = to_svg({"nodes": [{"id":"n", "x":100,"y":100,"label":"A & <B>"}], "edges":[]})
        self.assertIn("A &amp; &lt;B&gt;", xml)
        self.assertNotIn("A & <B>", xml)
    def test_link(self):
        xml = to_svg({"nodes":[{"id":"a","x":10,"y":20},{"id":"b","x":50,"y":60}],"edges":[{"from":"a","to":"b"}]})
        self.assertIn('x1="10"', xml)
        self.assertIn('x2="50"', xml)
