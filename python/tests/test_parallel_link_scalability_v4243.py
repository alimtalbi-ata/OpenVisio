"""V42.43 SAN multipath validator regression on the GitHub Python baseline."""
import time
import unittest
from openvisio.validation import validate_document


def topology(n):
    return {"nodes": [{"id": "a", "x": 0, "y": 0}, {"id": "b", "x": 100, "y": 0}],
            "edges": [{"id": f"fc{i}", "from": "a", "to": "b", "protocol": "FC",
                       "source_port": f"vmhba{i}", "target_port": f"fc{i}", "fabric": "A"}
                      for i in range(n)]}


class LinearMultipathTests(unittest.TestCase):
    def test_5000_distinct_paths(self):
        doc = topology(5000)
        start = time.monotonic()
        self.assertEqual(len(validate_document(doc)["edges"]), 5000)
        self.assertLess(time.monotonic() - start, 8.0)

    def test_duplicate_port_pair_rejected(self):
        doc = topology(300)
        doc["edges"].append({**doc["edges"][42], "id": "duplicate"})
        with self.assertRaises(ValueError):
            validate_document(doc)

    def test_unqualified_link_is_not_silently_multiplied(self):
        doc = topology(2)
        doc["edges"][0] = {"id": "unqualified", "from": "a", "to": "b"}
        with self.assertRaises(ValueError):
            validate_document(doc)

    def test_sheet_provenance_without_fabricated_ports(self):
        doc = topology(2)
        for i, edge in enumerate(doc["edges"]):
            edge.pop("source_port"); edge.pop("target_port")
            edge["visio_connector_sheet_id"] = str(i + 1)
        self.assertEqual(len(validate_document(doc)["edges"]), 2)

    def test_bad_port_metadata_rejected_as_value_error(self):
        doc = topology(1)
        doc["edges"][0]["source_port"] = ["bad"]
        with self.assertRaises(ValueError):
            validate_document(doc)


if __name__ == "__main__":
    unittest.main()
