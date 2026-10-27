"""Bounded, dimension-aware subset of Visio ShapeSheet geometry formulas.

Only scalar length/angle geometry is implemented, including basic comparisons
and lazy IF(condition, when_true, when_false) branches. Unsupported, cyclic,
mixed-dimension, non-finite, or over-budget expressions are refused so the
VSDX importer can retain cached V values and report the fidelity loss. This is
not a complete Visio interpreter. Author: Abdelhalim Talbi.
"""
from __future__ import annotations

import math
import re
from collections.abc import Mapping
from dataclasses import dataclass
from typing import Callable

GEOMETRY_CELL_NAMES = frozenset({"PinX", "PinY", "Width", "Height", "LocPinX", "LocPinY", "Angle"})
_LENGTH_CELL_NAMES = frozenset(name.casefold() for name in GEOMETRY_CELL_NAMES if name != "Angle")
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
    "nm": 1852.0 / 0.0254, "nauticalmile": 1852.0 / 0.0254,
    "nauticalmiles": 1852.0 / 0.0254,
    "yd": 36.0, "yard": 36.0, "yards": 36.0,
    "pt": 1.0 / 72.0, "point": 1.0 / 72.0, "points": 1.0 / 72.0,
    "p": 1.0 / 6.0, "pica": 1.0 / 6.0, "picas": 1.0 / 6.0,
}
_ANGLE_UNIT_FACTORS = {
    "deg": math.pi / 180.0, "degree": math.pi / 180.0,
    "degrees": math.pi / 180.0,
    "rad": 1.0, "radian": 1.0, "radians": 1.0,
}
# Universal implicit units are already in internal units. DL/DP mean inches,
# DA means radians. Duration/text units are outside this geometry-only subset.
_IMPLICIT_UNIT_DIMENSIONS = {"dl": "length", "dp": "length", "da": "angle"}
_TOKEN_RE = re.compile(
    r"\s*(?:(?P<number>(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
    r"|(?P<identifier>[A-Za-z_][A-Za-z0-9_.]*(?:![A-Za-z_][A-Za-z0-9_.]*)?)"
    r"|(?P<operator>>=|<=|<>|!=|==|\*\*|[><=()+\-*/^,\[\]]))"
)


class FormulaEvaluationError(ValueError):
    """Formula is outside the deliberately small supported subset."""


@dataclass(frozen=True)
class _Quantity:
    value: float
    # None means an unqualified value whose unit is inferred from cell context.
    # Internal values are inches/radians once a dimension is known.
    dimension: str | None = None


def _quantity(value: object) -> _Quantity:
    if isinstance(value, _Quantity):
        return value
    return _Quantity(_number(value))


def _merge_add_dimension(left: _Quantity, right: _Quantity) -> str | None:
    if left.dimension and right.dimension and left.dimension != right.dimension:
        raise FormulaEvaluationError("incompatible length/angle addition")
    return left.dimension or right.dimension



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
    def __init__(self, expression: str, resolve: Callable[[str], object]):
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
        self.syntax_only = False

    def peek(self, value: str | None = None) -> bool:
        return self.i < len(self.tokens) and (value is None or self.tokens[self.i][1] == value)

    def take(self, value: str | None = None) -> tuple[str, str]:
        if not self.peek(value):
            raise FormulaEvaluationError("unexpected formula token")
        token = self.tokens[self.i]
        self.i += 1
        return token

    def parse(self) -> _Quantity:
        result = self.comparison()
        if self.i != len(self.tokens):
            raise FormulaEvaluationError("trailing formula token")
        return _Quantity(_checked(result.value), result.dimension)

    def comparison(self) -> _Quantity:
        """Parse at most one relational comparison, below arithmetic precedence.

        ShapeSheet comparison results are represented as numeric booleans
        (1.0/0.0). Lengths and angles are compared only with like dimensions;
        an unqualified numeric operand inherits the other operand's context.
        Chained comparisons are intentionally rejected instead of guessed.
        """
        left = self.sum()
        if not any(self.peek(op) for op in (">=", "<=", "<>", "!=", "==", "<", ">", "=")):
            return left
        operator = self.take()[1]
        right = self.sum()
        if self.syntax_only:
            return _Quantity(1.0)
        _merge_add_dimension(left, right)  # Reject length/angle comparisons.
        if operator in ("=", "=="):
            matched = left.value == right.value
        elif operator in ("!=", "<>"):
            matched = left.value != right.value
        elif operator == "<":
            matched = left.value < right.value
        elif operator == ">":
            matched = left.value > right.value
        elif operator == "<=":
            matched = left.value <= right.value
        else:  # >=
            matched = left.value >= right.value
        return _Quantity(1.0 if matched else 0.0)

    def skip_argument(self) -> None:
        """Skip one unselected IF argument without resolving/evaluating it.

        Delimiters nested in function calls or universal-unit brackets are
        not treated as IF separators. Lexical errors have already been rejected
        by the tokenizer. Empty and unbalanced branches are still rejected.
        """
        start = self.i
        parens = 0
        brackets = 0
        while self.i < len(self.tokens):
            token = self.tokens[self.i][1]
            if token == "(":
                parens += 1
                if self.depth + parens > MAX_FORMULA_NESTING:
                    raise FormulaEvaluationError("formula nesting too deep")
            elif token == ")":
                if brackets:
                    raise FormulaEvaluationError("unbalanced unit bracket in conditional branch")
                if parens == 0:
                    break  # Leave the outer IF close for the caller.
                parens -= 1
            elif token == "[":
                brackets += 1
            elif token == "]":
                brackets -= 1
                if brackets < 0:
                    raise FormulaEvaluationError("unbalanced unit bracket in conditional branch")
            elif token == "," and parens == 0 and brackets == 0:
                break
            self.i += 1
        if self.i == start:
            raise FormulaEvaluationError("empty conditional branch")
        if parens or brackets:
            raise FormulaEvaluationError("unbalanced conditional branch")
        # Ensure an unselected expression is grammatically valid without
        # resolving references, computing arithmetic or invoking functions.
        validator = object.__new__(_Parser)
        validator.resolve = lambda _: _Quantity(1.0)
        validator.tokens = self.tokens[start:self.i]
        validator.i = 0
        validator.depth = self.depth
        validator.syntax_only = True
        validator.parse()

    def sum(self) -> _Quantity:
        result = self.product()
        while self.peek("+") or self.peek("-"):
            op = self.take()[1]
            right = self.product()
            if self.syntax_only:
                result = _Quantity(1.0)
                continue
            dimension = _merge_add_dimension(result, right)
            value = result.value + right.value if op == "+" else result.value - right.value
            result = _Quantity(_checked(value), dimension)
        return result

    def product(self) -> _Quantity:
        result = self.unary()
        while self.peek("*") or self.peek("/"):
            op = self.take()[1]
            right = self.unary()
            if self.syntax_only:
                result = _Quantity(1.0)
                continue
            if op == "*":
                if result.dimension and right.dimension:
                    raise FormulaEvaluationError("compound unit multiplication is unsupported")
                dimension = result.dimension or right.dimension
                result = _Quantity(_checked(result.value * right.value), dimension)
            else:
                if right.value == 0:
                    raise FormulaEvaluationError("division by zero")
                if result.dimension and right.dimension:
                    if result.dimension != right.dimension:
                        raise FormulaEvaluationError("incompatible length/angle division")
                    dimension = None
                elif right.dimension:
                    raise FormulaEvaluationError("inverse dimensional unit is unsupported")
                else:
                    dimension = result.dimension
                result = _Quantity(_checked(result.value / right.value), dimension)
        return result

    def unary(self) -> _Quantity:
        if self.peek("+"):
            self.take("+")
            return self.unary()
        if self.peek("-"):
            self.take("-")
            value = self.unary()
            return _Quantity(_checked(-value.value), value.dimension)
        return self.power()

    def power(self) -> _Quantity:
        result = self.atom()
        if self.peek("^") or self.peek("**"):
            self.take()
            exponent = self.unary()
            if self.syntax_only:
                result = _Quantity(1.0)
                return result
            if exponent.dimension:
                raise FormulaEvaluationError("dimensional exponent is unsupported")
            if result.dimension and exponent.value not in (0, 1):
                raise FormulaEvaluationError("compound dimensional power is unsupported")
            try:
                value = _checked(result.value ** exponent.value)
            except (OverflowError, ValueError, ZeroDivisionError) as exc:
                raise FormulaEvaluationError("invalid exponentiation") from exc
            dimension = result.dimension if exponent.value == 1 else None
            result = _Quantity(value, dimension)
        return result

    @staticmethod
    def _unit(unit: str, flag: str | None = None) -> _Quantity:
        key = unit.casefold().rstrip(".")
        factor = _LENGTH_UNIT_FACTORS.get(key)
        dimension = "length" if factor is not None else None
        if factor is None:
            factor = _ANGLE_UNIT_FACTORS.get(key)
            if factor is not None:
                dimension = "angle"
        if factor is None or dimension is None:
            raise FormulaEvaluationError("unsupported unit literal")
        if flag is not None:
            normalized_flag = flag.casefold()
            if normalized_flag not in {"a", "d", "p", "t"}:
                raise FormulaEvaluationError("unsupported implicit-unit flag")
            if (dimension == "angle") != (normalized_flag == "a"):
                raise FormulaEvaluationError("unit/implicit-flag dimension mismatch")
        return _Quantity(factor, dimension)

    def atom(self) -> _Quantity:
        if self.peek("("):
            self.take("(")
            self.depth += 1
            if self.depth > MAX_FORMULA_NESTING:
                raise FormulaEvaluationError("formula nesting too deep")
            try:
                result = self.comparison()
                self.take(")")
                return result
            finally:
                self.depth -= 1
        kind, value = self.take()
        if kind == "number":
            if self.syntax_only:
                if self.peek("["):
                    self.take("[")
                    unit_kind, unit = self.take()
                    if unit_kind != "identifier":
                        raise FormulaEvaluationError("unit name expected")
                    self.take(",")
                    flag_kind, flag = self.take()
                    if flag_kind != "identifier":
                        raise FormulaEvaluationError("implicit-unit flag expected")
                    self.take("]")
                    self._unit(unit, flag)
                    return _Quantity(1.0)
                if self.peek() and self.tokens[self.i][0] == "identifier":
                    unit = self.tokens[self.i][1].casefold().rstrip(".")
                    if unit in _LENGTH_UNIT_FACTORS or unit in _ANGLE_UNIT_FACTORS:
                        self.take()
                        self._unit(unit)
                    elif unit in _IMPLICIT_UNIT_DIMENSIONS:
                        self.take()
                return _Quantity(1.0)
            result = _Quantity(_checked(float(value)))
            # Universal syntax: 5[deg,A], 5[in,D], 2[ft,P].
            # Supported geometry values normalize to internal inches/radians.
            if self.peek("["):
                self.take("[")
                unit_kind, unit = self.take()
                if unit_kind != "identifier":
                    raise FormulaEvaluationError("unit name expected")
                self.take(",")
                flag_kind, flag = self.take()
                if flag_kind != "identifier":
                    raise FormulaEvaluationError("implicit-unit flag expected")
                self.take("]")
                converted = self._unit(unit, flag)
                result = _Quantity(_checked(result.value * converted.value), converted.dimension)
                return result
            # Explicit suffixes such as 2400 mm normalize to internal units.
            if self.peek() and self.tokens[self.i][0] == "identifier":
                unit = self.tokens[self.i][1].casefold().rstrip(".")
                if unit in _LENGTH_UNIT_FACTORS or unit in _ANGLE_UNIT_FACTORS:
                    self.take()
                    converted = self._unit(unit)
                    result = _Quantity(_checked(result.value * converted.value), converted.dimension)
                elif unit in _IMPLICIT_UNIT_DIMENSIONS:
                    self.take()
                    result = _Quantity(result.value, _IMPLICIT_UNIT_DIMENSIONS[unit])
            return result
        if kind != "identifier":
            raise FormulaEvaluationError("number or cell reference expected")
        name = value.upper()
        if name in {"NAN", "INF", "INFINITY"} and not self.syntax_only:
            raise FormulaEvaluationError("non-finite literal is not supported")
        if self.peek("("):
            self.take("(")
            self.depth += 1
            if self.depth > MAX_FORMULA_NESTING:
                raise FormulaEvaluationError("formula nesting too deep")
            try:
                if name == "IF":
                    if self.syntax_only:
                        # Syntax-only validation checks both branches but does
                        # not resolve or evaluate either one.
                        self.comparison()
                        self.take(",")
                        self.comparison()
                        self.take(",")
                        self.comparison()
                        self.take(")")
                        return _Quantity(1.0)
                    # IF is deliberately lazy: an unsupported dependency or a
                    # divide-by-zero in the unselected branch must not poison
                    # otherwise valid geometry. The skipped branch receives a
                    # syntax-only parse to avoid accepting malformed formulas.
                    condition = self.comparison()
                    self.take(",")
                    if condition.value != 0:
                        chosen = self.comparison()
                        self.take(",")
                        self.skip_argument()
                    else:
                        self.skip_argument()
                        self.take(",")
                        chosen = self.comparison()
                    self.take(")")
                    return chosen
                args = []
                if not self.peek(")"):
                    while True:
                        args.append(self.sum())
                        if self.peek(","):
                            self.take(",")
                            continue
                        break
                self.take(")")
                if self.syntax_only:
                    return _Quantity(1.0)
                return self.call(name, args)
            finally:
                self.depth -= 1
        if name == "PI":
            return _Quantity(1.0 if self.syntax_only else math.pi)
        if self.syntax_only:
            return _Quantity(1.0)
        return _quantity(self.resolve(value))

    @staticmethod
    def call(name: str, args: list[_Quantity]) -> _Quantity:
        if name in {"GUARD", "THEMEGUARD"} and len(args) == 1:
            return args[0]
        if name == "PI" and not args:
            return _Quantity(math.pi)
        if name == "ABS" and len(args) == 1:
            return _Quantity(_checked(abs(args[0].value)), args[0].dimension)
        if name == "SQRT" and len(args) == 1 and args[0].value >= 0:
            if args[0].dimension:
                raise FormulaEvaluationError("square root of dimensional value is unsupported")
            return _Quantity(_checked(math.sqrt(args[0].value)))
        if name in {"MIN", "MAX"} and args:
            dimension = None
            for arg in args:
                if dimension and arg.dimension and dimension != arg.dimension:
                    raise FormulaEvaluationError("MIN/MAX mixes length and angle")
                dimension = dimension or arg.dimension
            chosen = min(args, key=lambda item: item.value) if name == "MIN" else max(args, key=lambda item: item.value)
            return _Quantity(_checked(chosen.value), dimension)
        functions = {"SIN": math.sin, "COS": math.cos, "TAN": math.tan,
                     "ASIN": math.asin, "ACOS": math.acos, "ATAN": math.atan}
        if name in functions and len(args) == 1:
            arg = args[0]
            inverse = name in {"ASIN", "ACOS", "ATAN"}
            if inverse and arg.dimension:
                raise FormulaEvaluationError("inverse trigonometry requires a scalar")
            if not inverse and arg.dimension == "length":
                raise FormulaEvaluationError("trigonometry cannot consume a length")
            try:
                result = _checked(functions[name](arg.value))
            except (ValueError, OverflowError) as exc:
                raise FormulaEvaluationError("invalid math function argument") from exc
            return _Quantity(result, "angle" if inverse else None)
        raise FormulaEvaluationError("unsupported formula function or arity")


def evaluate_numeric_formula(expression: str, resolve: Callable[[str], object]) -> float:
    """Evaluate bounded arithmetic without eval, imports, or code execution.

    Unit-tagged intermediate values are checked for incompatible dimensions;
    the public scalar API returns the normalized numeric component.
    """
    return _Parser(expression, resolve).parse().value


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


def _cell_dimension(name: str) -> str | None:
    folded = str(name).casefold()
    if folded == "angle":
        return "angle"
    if folded in _LENGTH_CELL_NAMES:
        return "length"
    return None


def _evaluate_geometry_formula(expression: str, resolve: Callable[[str], object], expected: str) -> _Quantity:
    value = _Parser(expression.strip(), resolve).parse()
    if value.dimension is not None and value.dimension != expected:
        raise FormulaEvaluationError(f"formula result is {value.dimension}, expected {expected}")
    # Formulas without explicit dimensions use the target cell's default unit.
    return _Quantity(_checked(value.value), expected)


def evaluate_geometry_formula_cells(
    values: Mapping[str, object], formulas: Mapping[str, object],
    page_values: Mapping[str, object] | None = None,
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Evaluate geometry formulas all-or-none with case and unit validation.

    Length cells are normalized to inches, angle cells to radians. Explicit
    length/angle units cannot be silently mixed, and dimension-mismatched
    results are refused rather than corrupting imported shape geometry.
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
    if any(len(entries) != 1 for entries in target_index.values()):
        return {}, tuple(sorted(targets))

    formula_index = _casefold_index(formulas)
    value_index = _casefold_index(values)
    page_index = _casefold_index(page_values or {})
    target_name_by_fold = {folded: entries[0][0] for folded, entries in target_index.items()}
    resolved: dict[str, float] = {}
    active: set[str] = set()

    def resolve(name: str) -> _Quantity:
        if "!" in name:
            object_name, cell_name = name.split("!", 1)
            if object_name.casefold() == "thepage":
                folded_cell = cell_name.casefold()
                if folded_cell not in {"pagewidth", "pageheight"}:
                    raise FormulaEvaluationError("unsupported page-cell reference")
                value = _unique_casefold_value(page_index, folded_cell, "page-cell")
                return _Quantity(_number(value), "length")

        folded = name.casefold()
        if folded in target_name_by_fold:
            target_name = target_name_by_fold[folded]
            if target_name in resolved:
                return _Quantity(resolved[target_name], _cell_dimension(target_name))
            if folded in active:
                raise FormulaEvaluationError("cyclic geometry formula")
            active.add(folded)
            try:
                expected = _cell_dimension(target_name)
                value = _evaluate_geometry_formula(targets[target_name], resolve, expected)
                resolved[target_name] = _checked(value.value)
                return _Quantity(resolved[target_name], expected)
            finally:
                active.discard(folded)

        if folded in formula_index:
            _unique_casefold_value(formula_index, folded, "formula-cell")
            raise FormulaEvaluationError("formula-bearing non-geometry dependency")
        if folded in value_index:
            value = _number(_unique_casefold_value(value_index, folded, "cached-cell"))
            return _Quantity(value, _cell_dimension(folded))
        raise FormulaEvaluationError("unknown ShapeSheet cell reference")

    unresolved = []
    for name in sorted(targets):
        try:
            resolve(name)
        except (FormulaEvaluationError, ValueError, TypeError, OverflowError, RecursionError):
            unresolved.append(name)
    return ({}, tuple(unresolved)) if unresolved else (dict(resolved), ())
