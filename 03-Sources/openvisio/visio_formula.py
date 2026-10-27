"""Bounded scalar subset of Visio ShapeSheet geometry formulas.
Unsupported, cyclic, non-finite, or over-budget expressions are refused; import can
then keep cached V values and report the loss. This is not a complete Visio interpreter.
Author: Abdelhalim Talbi.
"""
from __future__ import annotations
import math
import re
from collections.abc import Mapping
from typing import Callable

GEOMETRY_CELL_NAMES = frozenset({"PinX", "PinY", "Width", "Height", "LocPinX", "LocPinY", "Angle"})
MAX_FORMULA_CHARS = 512
MAX_FORMULA_TOKENS = 256
MAX_FORMULA_NESTING = 32
MAX_INTERMEDIATE_MAGNITUDE = 1.0e12

# Universal ShapeSheet units used in position, size and angle formulas. Lengths
# normalize to inches and angles to radians, the internal coordinates consumed
# by the VSDX geometry reader. A suffix is recognized only immediately after a
# numeric literal; unknown suffixes remain syntax errors.
_LENGTH_UNIT_FACTORS = {
    "in": 1.0, "inch": 1.0, "inches": 1.0, "i": 1.0,
    "ft": 12.0, "foot": 12.0, "feet": 12.0, "f": 12.0,
    "cm": 1.0 / 2.54,
    "mm": 1.0 / 25.4,
    "m": 100.0 / 2.54, "meter": 100.0 / 2.54,
    "meters": 100.0 / 2.54, "metre": 100.0 / 2.54,
    "metres": 100.0 / 2.54,
    "km": 100000.0 / 2.54,
    "mi": 63360.0, "mile": 63360.0, "miles": 63360.0,
    "yd": 36.0, "yard": 36.0, "yards": 36.0,
    "pt": 1.0 / 72.0, "point": 1.0 / 72.0, "points": 1.0 / 72.0,
}
_ANGLE_UNIT_FACTORS = {
    "deg": math.pi / 180.0, "degree": math.pi / 180.0,
    "degrees": math.pi / 180.0,
    "rad": 1.0, "radian": 1.0, "radians": 1.0,
}
_TOKEN_RE = re.compile(
    r"\s*(?:(?P<number>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<identifier>[A-Za-z_][A-Za-z0-9_.]*(?:![A-Za-z_][A-Za-z0-9_.]*)?)"
    r"|(?P<operator>\*\*|[()+\-*/^,]))"
)


class FormulaEvaluationError(ValueError):
    """Formula is outside the deliberately small supported subset."""


def _checked(value: float) -> float:
    # ShapeSheet scalar geometry is real-valued. Python exponentiation can
    # produce a complex result (for example (-1)^0.5); normalize that to the
    # same conservative refusal path as every other unsupported expression.
    try:
        value = float(value)
    except (TypeError, ValueError, OverflowError) as exc:
        raise FormulaEvaluationError("non-real numeric result") from exc
    if not math.isfinite(value) or abs(value) > MAX_INTERMEDIATE_MAGNITUDE:
        raise FormulaEvaluationError("non-finite or out-of-bounds intermediate")
    return value


def _number(value: object) -> float:
    try:
        return _checked(float(value))
    except (TypeError, ValueError, OverflowError) as exc:
        raise FormulaEvaluationError("non-numeric cell reference") from exc


class _Parser:
    def __init__(self, expression: str, resolve: Callable[[str], float]):
        if not isinstance(expression, str) or not expression.strip():
            raise FormulaEvaluationError("empty formula")
        if len(expression) > MAX_FORMULA_CHARS:
            raise FormulaEvaluationError("formula too long")
        self.resolve = resolve
        self.tokens: list[tuple[str, str]] = []
        pos = 0
        while pos < len(expression):
            match = _TOKEN_RE.match(expression, pos)
            if match is None:
                if not expression[pos:].strip():
                    break
                raise FormulaEvaluationError("unsupported token")
            kind = ("number" if match.group("number") is not None else
                    "identifier" if match.group("identifier") is not None else "operator")
            self.tokens.append((kind, match.group(kind)))
            if len(self.tokens) > MAX_FORMULA_TOKENS:
                raise FormulaEvaluationError("too many formula tokens")
            pos = match.end()
        self.i = 0
        self.depth = 0

    def peek(self, value: str | None = None) -> bool:
        return self.i < len(self.tokens) and (value is None or self.tokens[self.i][1] == value)

    def take(self, value: str | None = None) -> tuple[str, str]:
        if not self.peek(value):
            raise FormulaEvaluationError("unexpected formula token")
        token = self.tokens[self.i]
        self.i += 1
        return token

    def parse(self) -> float:
        result = self.sum()
        if self.i != len(self.tokens):
            raise FormulaEvaluationError("trailing formula token")
        return _checked(result)

    def sum(self) -> float:
        result = self.product()
        while self.peek("+") or self.peek("-"):
            op = self.take()[1]
            right = self.product()
            result = _checked(result + right if op == "+" else result - right)
        return result

    def product(self) -> float:
        result = self.unary()
        while self.peek("*") or self.peek("/"):
            op = self.take()[1]
            right = self.unary()
            if op == "*":
                result = _checked(result * right)
            else:
                if right == 0:
                    raise FormulaEvaluationError("division by zero")
                result = _checked(result / right)
        return result

    def unary(self) -> float:
        if self.peek("+"):
            self.take("+")
            return self.unary()
        if self.peek("-"):
            self.take("-")
            return _checked(-self.unary())
        return self.power()

    def power(self) -> float:
        result = self.atom()
        if self.peek("^") or self.peek("**"):
            self.take()
            exponent = self.unary()
            try:
                result = _checked(result ** exponent)
            except (OverflowError, ValueError, ZeroDivisionError) as exc:
                raise FormulaEvaluationError("invalid exponentiation") from exc
        return result

    def atom(self) -> float:
        if self.peek("("):
            self.take("(")
            self.depth += 1
            if self.depth > MAX_FORMULA_NESTING:
                raise FormulaEvaluationError("formula nesting too deep")
            try:
                result = self.sum()
                self.take(")")
                return _checked(result)
            finally:
                self.depth -= 1
        kind, value = self.take()
        if kind == "number":
            result = _checked(float(value))
            # ShapeSheet commonly spells literals as ``2400 mm`` or ``90 deg``.
            # The lexer keeps the suffix as an identifier; only recognized units
            # immediately after a numeric literal are consumed here.
            if self.peek() and self.tokens[self.i][0] == "identifier":
                unit = self.tokens[self.i][1].casefold().rstrip(".")
                factor = _LENGTH_UNIT_FACTORS.get(unit)
                if factor is None:
                    factor = _ANGLE_UNIT_FACTORS.get(unit)
                if factor is not None:
                    self.take()
                    result = _checked(result * factor)
            return result
        if kind != "identifier":
            raise FormulaEvaluationError("number or cell reference expected")
        name = value.upper()
        if name in {"NAN", "INF", "INFINITY"}:
            raise FormulaEvaluationError("non-finite literal is not supported")
        if self.peek("("):
            self.take("(")
            self.depth += 1
            if self.depth > MAX_FORMULA_NESTING:
                raise FormulaEvaluationError("formula nesting too deep")
            try:
                args = []
                if not self.peek(")"):
                    while True:
                        args.append(self.sum())
                        if self.peek(","):
                            self.take(",")
                            continue
                        break
                self.take(")")
                return _checked(self.call(name, args))
            finally:
                self.depth -= 1
        if name == "PI":
            return math.pi
        return _checked(self.resolve(value))

    @staticmethod
    def call(name: str, args: list[float]) -> float:
        if name in {"GUARD", "THEMEGUARD"} and len(args) == 1:
            return args[0]
        if name == "PI" and not args:
            return math.pi
        if name == "ABS" and len(args) == 1:
            return abs(args[0])
        if name == "SQRT" and len(args) == 1 and args[0] >= 0:
            return math.sqrt(args[0])
        if name in {"MIN", "MAX"} and args:
            return min(args) if name == "MIN" else max(args)
        functions = {"SIN": math.sin, "COS": math.cos, "TAN": math.tan,
                     "ASIN": math.asin, "ACOS": math.acos, "ATAN": math.atan}
        if name in functions and len(args) == 1:
            try:
                return _checked(functions[name](args[0]))
            except (ValueError, OverflowError) as exc:
                raise FormulaEvaluationError("invalid math function argument") from exc
        raise FormulaEvaluationError("unsupported formula function or arity")


def evaluate_numeric_formula(expression: str, resolve: Callable[[str], float]) -> float:
    """Evaluate bounded arithmetic without eval, imports, attribute access, or code execution."""
    return _Parser(expression, resolve).parse()


def _casefold_index(mapping: Mapping[str, object]) -> dict[str, list[tuple[str, object]]]:
    """Index ShapeSheet names without losing evidence of ambiguous case aliases."""
    index: dict[str, list[tuple[str, object]]] = {}
    for key, value in mapping.items():
        spelling = str(key)
        index.setdefault(spelling.casefold(), []).append((spelling, value))
    return index


def _unique_casefold_value(
    index: Mapping[str, list[tuple[str, object]]], folded_name: str, description: str,
) -> object:
    """Return one case-insensitive entry; refuse missing or colliding aliases."""
    matches = index.get(folded_name, ())
    if not matches:
        raise FormulaEvaluationError(f"unknown {description} reference")
    if len(matches) != 1:
        raise FormulaEvaluationError(f"ambiguous case-insensitive {description} reference")
    return matches[0][1]


def evaluate_geometry_formula_cells(
    values: Mapping[str, object], formulas: Mapping[str, object],
    page_values: Mapping[str, object] | None = None,
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Evaluate geometry formulas all-or-none using case-insensitive cell names.

    Microsoft ShapeSheet references are normalized by cell spelling, not by the
    capitalization used by a formula author. Case-fold collisions are refused
    rather than resolved by dictionary iteration order. A failed dependency
    rejects the whole candidate geometry set so callers can safely keep cached
    V values and report the limitation.
    """
    geometry_names = {name.casefold() for name in GEOMETRY_CELL_NAMES}
    targets = {
        str(key): str(expression)
        for key, expression in formulas.items()
        if str(key).casefold() in geometry_names and expression is not None
    }
    if not targets:
        return {}, ()

    target_index = _casefold_index(targets)
    # Two formula cells that differ only by case are ambiguous even if only one
    # would happen to be reached first. Never let input ordering select a cell.
    if any(len(entries) != 1 for entries in target_index.values()):
        return {}, tuple(sorted(targets))

    formula_index = _casefold_index(formulas)
    value_index = _casefold_index(values)
    page_index = _casefold_index(page_values or {})
    target_name_by_fold = {folded: entries[0][0] for folded, entries in target_index.items()}
    resolved: dict[str, float] = {}
    active: set[str] = set()

    def resolve(name: str) -> float:
        if "!" in name:
            object_name, cell_name = name.split("!", 1)
            if object_name.casefold() == "thepage":
                folded_cell = cell_name.casefold()
                if folded_cell not in {"pagewidth", "pageheight"}:
                    raise FormulaEvaluationError("unsupported page-cell reference")
                value = _unique_casefold_value(page_index, folded_cell, "page-cell")
                return _number(value)

        folded = name.casefold()
        if folded in target_name_by_fold:
            target_name = target_name_by_fold[folded]
            if target_name in resolved:
                return resolved[target_name]
            if folded in active:
                raise FormulaEvaluationError("cyclic geometry formula")
            active.add(folded)
            try:
                value = evaluate_numeric_formula(targets[target_name].strip(), resolve)
                resolved[target_name] = _checked(value)
                return resolved[target_name]
            finally:
                active.discard(folded)

        # A formula-bearing non-geometry dependency must never be mistaken for
        # its cached V value, even when the formula changes capitalization.
        if folded in formula_index:
            _unique_casefold_value(formula_index, folded, "formula-cell")
            raise FormulaEvaluationError("formula-bearing non-geometry dependency")
        if folded in value_index:
            return _number(_unique_casefold_value(value_index, folded, "cached-cell"))
        raise FormulaEvaluationError("unknown ShapeSheet cell reference")

    unresolved = []
    for name in sorted(targets):
        try:
            resolve(name)
        except (FormulaEvaluationError, ValueError, TypeError, OverflowError, RecursionError):
            unresolved.append(name)
    return ({}, tuple(unresolved)) if unresolved else (dict(resolved), ())
