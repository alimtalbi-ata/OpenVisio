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
            return _checked(float(value))
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


def evaluate_geometry_formula_cells(
    values: Mapping[str, object], formulas: Mapping[str, object],
    page_values: Mapping[str, object] | None = None,
) -> tuple[dict[str, float], tuple[str, ...]]:
    """Evaluate geometry formulas all-or-none; return unresolved target names on failure."""
    targets = {str(k): str(v) for k, v in formulas.items()
               if k in GEOMETRY_CELL_NAMES and v is not None}
    if not targets:
        return {}, ()
    page_values = page_values or {}
    resolved: dict[str, float] = {}
    active: set[str] = set()

    def resolve(name: str) -> float:
        if name.startswith("ThePage!"):
            cell = name.split("!", 1)[1]
            if cell not in {"PageWidth", "PageHeight"} or cell not in page_values:
                raise FormulaEvaluationError("unsupported page-cell reference")
            return _number(page_values[cell])
        if name in targets:
            if name in resolved:
                return resolved[name]
            if name in active:
                raise FormulaEvaluationError("cyclic geometry formula")
            active.add(name)
            try:
                value = evaluate_numeric_formula(targets[name].strip(), resolve)
                resolved[name] = _checked(value)
                return resolved[name]
            finally:
                active.discard(name)
        if name in formulas:
            raise FormulaEvaluationError("formula-bearing non-geometry dependency")
        if name not in values:
            raise FormulaEvaluationError("unknown ShapeSheet cell reference")
        return _number(values[name])

    unresolved = []
    for name in sorted(targets):
        try:
            resolve(name)
        except (FormulaEvaluationError, ValueError, TypeError, OverflowError, RecursionError):
            unresolved.append(name)
    return ({}, tuple(unresolved)) if unresolved else (dict(resolved), ())
