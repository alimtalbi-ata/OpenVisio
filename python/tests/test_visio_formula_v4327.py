"""Tests for the bounded ShapeSheet scalar formula subset. Author: Abdelhalim Talbi."""
import unittest
from openvisio.visio_formula import FormulaEvaluationError, evaluate_geometry_formula_cells, evaluate_numeric_formula


class NumericFormulaTests(unittest.TestCase):
    def test_guarded_page_dimension_arithmetic(self):
        self.assertEqual(evaluate_numeric_formula(
            "GUARD(ThePage!PageWidth*0.5+1/4)",
            lambda name: {"ThePage!PageWidth": 8.5}[name]), 4.5)

    def test_operator_precedence_and_negative_exponent(self):
        self.assertEqual(evaluate_numeric_formula("-2^2 + 10", lambda _: 0), 6)
        self.assertAlmostEqual(evaluate_numeric_formula("2^-2", lambda _: 0), 0.25)

    def test_whitelisted_functions(self):
        self.assertAlmostEqual(evaluate_numeric_formula(
            "MAX(ABS(-3), SQRT(16), PI()/2)", lambda _: 0), 4.0)

    def test_formula_cell_dependency_resolves_in_order(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"PinY": "3", "Width": "4", "Height": "2"},
            {"PinX": "GUARD(Width*0.5)", "LocPinX": "Width/2"})
        self.assertEqual(unresolved, ())
        self.assertEqual(actual, {"PinX": 2.0, "LocPinX": 2.0})

    def test_page_references_are_explicitly_scoped(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"PinY": "1"}, {"PinX": "ThePage!PageWidth/2"}, {"PageWidth": "10"})
        self.assertEqual(unresolved, ())
        self.assertEqual(actual["PinX"], 5)

    def test_unknown_formula_never_uses_cached_value_as_formula_result(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"PinX": "7"}, {"PinX": "UnsupportedFunction(7)"})
        self.assertEqual(actual, {})
        self.assertEqual(unresolved, ("PinX",))

    def test_cycle_rejects_the_whole_geometry_set(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"PinX": "8", "PinY": "9"}, {"PinX": "PinY+1", "PinY": "PinX+1"})
        self.assertEqual(actual, {})
        self.assertEqual(set(unresolved), {"PinX", "PinY"})

    def test_non_geometry_formula_dependency_is_not_read_from_cache(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"PinX": "7", "Prop.SomeFormula": "3"},
            {"PinX": "Prop.SomeFormula*2", "Prop.SomeFormula": "Width*2"})
        self.assertEqual(actual, {})
        self.assertEqual(unresolved, ("PinX",))

    def test_division_zero_injection_and_nonfinite_literals_are_rejected(self):
        for expression in ("1/0", "__import__('os').system('id')", "1;2", "NaN", "Infinity"):
            with self.subTest(expression=expression), self.assertRaises(FormulaEvaluationError):
                evaluate_numeric_formula(expression, lambda _: 0.0)

    def test_nonfinite_and_overlarge_results_are_rejected(self):
        for expression in ("1e999", "1e11*100", "SQRT(-1)", "(-1)^0.5"):
            with self.subTest(expression=expression), self.assertRaises(FormulaEvaluationError):
                evaluate_numeric_formula(expression, lambda _: 0.0)

    def test_explicit_length_units_normalize_to_inches(self):
        cases = {
            "1 in": 1.0,
            "2 ft": 24.0,
            "25.4 mm": 1.0,
            "2.54 cm": 1.0,
            "1 m": 100.0 / 2.54,
            "1 yd": 36.0,
            "72 pt": 1.0,
            "1 IN.": 1.0,
            "25.4mm": 1.0,
            "1e1 mm": 10.0 / 25.4,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertAlmostEqual(
                    evaluate_numeric_formula(expression, lambda _: 0.0), expected, places=10)

    def test_explicit_angle_units_normalize_to_radians(self):
        for expression, expected in (("180 deg", 3.141592653589793),
                                     ("90 degrees", 1.5707963267948966),
                                     ("1 rad", 1.0)):
            with self.subTest(expression=expression):
                self.assertAlmostEqual(
                    evaluate_numeric_formula(expression, lambda _: 0.0), expected, places=12)

    def test_unit_suffixes_work_inside_guard_and_arithmetic(self):
        self.assertAlmostEqual(evaluate_numeric_formula(
            "GUARD(1 ft + 6 in)", lambda _: 0.0), 18.0)
        self.assertAlmostEqual(evaluate_numeric_formula(
            "MAX(25.4 mm, 1 in) * 2", lambda _: 0.0), 2.0)

    def test_unknown_or_unattached_unit_suffix_is_rejected(self):
        for expression in ("1 furlong", "Width mm", "1 in nonsense"):
            with self.subTest(expression=expression), self.assertRaises(FormulaEvaluationError):
                evaluate_numeric_formula(expression, lambda _: 1.0)

    def test_token_and_nesting_limits_are_enforced(self):
        with self.assertRaises(FormulaEvaluationError):
            evaluate_numeric_formula("1+" * 130 + "1", lambda _: 0.0)
        expression = "(" * 40 + "1" + ")" * 40
        with self.assertRaises(FormulaEvaluationError):
            evaluate_numeric_formula(expression, lambda _: 0.0)


    def test_geometry_cell_references_ignore_formula_capitalization(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"wIdTh": "4", "HeIgHt": "2"},
            {"pInX": "gUaRd(wIDTH*0.5)", "lOcPiNx": "width/2"},
        )
        self.assertEqual(unresolved, ())
        self.assertEqual(actual, {"pInX": 2.0, "lOcPiNx": 2.0})

    def test_page_object_and_page_cell_references_ignore_case(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {}, {"PinX": "GUARD(tHePaGe!pAgEwIdTh*0.5)"},
            {"pAgEwIdTh": "10", "PAGEHEIGHT": "7"},
        )
        self.assertEqual(unresolved, ())
        self.assertEqual(actual, {"PinX": 5.0})

    def test_casefold_collision_in_geometry_targets_refuses_entire_set(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {}, {"PinX": "1", "pinx": "2", "PinY": "3"},
        )
        self.assertEqual(actual, {})
        self.assertEqual(set(unresolved), {"PinX", "pinx", "PinY"})

    def test_casefold_collision_in_cached_values_is_not_iteration_order_dependent(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"Width": "4", "wIdTh": "8"}, {"PinX": "width/2"},
        )
        self.assertEqual(actual, {})
        self.assertEqual(unresolved, ("PinX",))

    def test_non_geometry_formula_dependency_is_refused_case_insensitively(self):
        actual, unresolved = evaluate_geometry_formula_cells(
            {"Prop.Width": "4"},
            {"PinX": "pRoP.wIdTh*2", "prop.width": "Width/2"},
        )
        self.assertEqual(actual, {})
        self.assertEqual(unresolved, ("PinX",))

    def test_numeric_formula_resolution_callback_receives_original_spelling(self):
        seen = []
        value = evaluate_numeric_formula("wIdTh + 1", lambda name: seen.append(name) or 4)
        self.assertEqual(value, 5)


if __name__ == "__main__":
    unittest.main()
