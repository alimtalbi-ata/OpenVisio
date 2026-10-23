import unittest
from openvisio.templates import TEMPLATES, create_template
from openvisio.model import validate

class InfrastructureTemplateTests(unittest.TestCase):
    def test_all_templates_validate(self):
        for name in TEMPLATES:
            with self.subTest(name=name):
                self.assertTrue(validate(create_template(name)))
    def test_ids_are_unique_per_generation(self):
        a=create_template("SAN double fabric")
        b=create_template("SAN double fabric")
        self.assertTrue({n["id"] for n in a["nodes"]}.isdisjoint({n["id"] for n in b["nodes"]}))
    def test_unknown_template(self):
        with self.assertRaises(ValueError):
            create_template("unknown")
    def test_san_redundancy(self):
        doc=create_template("SAN double fabric")
        self.assertEqual(len(doc["nodes"]),5)
        self.assertEqual(len(doc["edges"]),6)
        self.assertTrue(all(e["protocol"]=="FC" for e in doc["edges"]))
