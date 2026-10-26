"""Fail-closed VSDX fidelity gate tests. Author: Abdelhalim Talbi."""
import unittest

from openvisio.vsdx import VsdxFidelityError, _require_reported_fidelity


LOSS_COUNTERS = (
    "rotated_shapes_as_bounding_boxes",
    "formula_driven_geometry_unresolved_shapes",
    "group_children_omitted",
    "group_children_imported",
    "page_extent_expanded",
    "orthogonal_connector_routes_approximated",
    "connector_links_skipped",
)


class StrictFidelityCounterTests(unittest.TestCase):
    def test_every_known_loss_counter_blocks_without_warning_text(self):
        for key in LOSS_COUNTERS:
            with self.subTest(counter=key):
                document = {"nodes": [], "edges": [], "metadata": {key: 1}}
                with self.assertRaises(VsdxFidelityError) as caught:
                    _require_reported_fidelity(document, strict_fidelity=True)
                self.assertTrue(any(key in issue for issue in caught.exception.issues),
                                caught.exception.issues)

    def test_all_positive_counters_are_checked_even_if_an_unrelated_warning_exists(self):
        document = {"nodes": [], "edges": [], "metadata": {
            "fidelity_warnings": ["unrelated diagnostic"],
            "formula_driven_geometry_unresolved_shapes": 2,
            "connector_links_skipped": 3,
        }}
        with self.assertRaises(VsdxFidelityError) as caught:
            _require_reported_fidelity(document, strict_fidelity=True)
        joined = " ".join(caught.exception.issues)
        self.assertIn("formula_driven_geometry_unresolved_shapes=2", joined)
        self.assertIn("connector_links_skipped=3", joined)

    def test_matching_warning_and_counter_are_not_reported_twice(self):
        warning = "2 rotated Visio shape(s) approximated by axis-aligned bounding boxes"
        document = {"nodes": [], "edges": [], "metadata": {
            "fidelity_warnings": [warning],
            "rotated_shapes_as_bounding_boxes": 2,
        }}
        with self.assertRaises(VsdxFidelityError) as caught:
            _require_reported_fidelity(document, strict_fidelity=True)
        self.assertEqual((warning,), caught.exception.issues)

    def test_zero_counters_do_not_create_a_false_fidelity_failure(self):
        document = {"nodes": [], "edges": [], "metadata": {
            **{key: 0 for key in LOSS_COUNTERS},
            "fidelity_warnings": [],
        }}
        self.assertIs(_require_reported_fidelity(document, strict_fidelity=True), document)

    def test_malformed_counters_fail_closed(self):
        for value in (True, -1, "1", 1.0):
            with self.subTest(value=value):
                document = {"nodes": [], "edges": [], "metadata": {
                    "group_children_omitted": value,
                }}
                with self.assertRaisesRegex(VsdxFidelityError, "Compteur de perte de fidélité invalide"):
                    _require_reported_fidelity(document, strict_fidelity=True)

    def test_non_strict_import_behavior_is_unchanged(self):
        document = {"nodes": [], "edges": [], "metadata": {
            "rotated_shapes_as_bounding_boxes": 1,
        }}
        self.assertIs(_require_reported_fidelity(document, strict_fidelity=False), document)


if __name__ == "__main__":
    unittest.main()
