from __future__ import annotations

from typing import Any

from ssn.ast import (
    ArrayTypeExpr,
    EnumTypeExpr,
    ObjectTypeExpr,
    PrimitiveTypeExpr,
    PropertyDef,
    Schema,
    TypeDef,
    TypeExpr,
    TypeRef,
)
from ssn.visitor import ExprVisitor, NodeVisitor


def _example_for_primitive_format(fmt: str | None) -> Any:
    """Return an example value for a primitive type by format name."""
    if fmt in ("integer", "int"):
        return 1
    if fmt in ("number", "float", "double"):
        return 1.0
    if fmt in ("boolean", "bool"):
        return True
    if fmt in ("UUID", "uuid", "guid"):
        return "00000000-0000-0000-0000-000000000000"
    if fmt in ("json", "object"):
        return {}
    return "string"


class _Missing:
    """Sentinel for 'no value' to distinguish from None/defaults."""


_MISSING = _Missing()


class ExampleBuilder(ExprVisitor, NodeVisitor):
    """Visitor that builds example data from Schema AST.

    Rules: use explicit default if present; nullable → None; enums → first value;
    arrays → one example item; objects → examples for each property; refs → resolved type.
    """

    def __init__(self) -> None:
        self._value: Any = None

    def build_for_schema(self, schema: Schema) -> dict[str, Any]:
        """Build example object for the root schema."""
        schema.visit(self)
        return self._value

    def build_for_property(self, prop: PropertyDef) -> Any:
        """Build example value for a single property."""
        prop.visit(self)
        return self._value

    def build_for_type_expr(self, expr: TypeExpr) -> Any:
        """Build example value for a type expression."""
        expr.visit(self)
        return self._value

    # NodeVisitor -----------------------------------------------------------------

    def visit_schema(self, schema: Schema) -> None:
        result: dict[str, Any] = {}
        for prop in schema.root:
            prop.visit(self)
            if self._value is _MISSING:
                continue
            result[prop.name] = self._value
        self._value = result

    def visit_type_def(self, type_def: TypeDef) -> None:
        type_def.expr.visit(self)

    def visit_property(self, prop: PropertyDef) -> None:
        if prop.default is not None:
            self._value = prop.default
            return
        if prop.nullable:
            self._value = None
            return
        prop.type.visit(self)

    # ExprVisitor -----------------------------------------------------------------

    def visit_ref(self, expr: TypeRef) -> None:
        if expr.resolved is None:
            self._value = None
            return
        expr.resolved.visit(self)

    def visit_object(self, expr: ObjectTypeExpr) -> None:
        result: dict[str, Any] = {}
        for name, prop in expr.properties.items():
            prop.visit(self)
            if self._value is _MISSING:
                continue
            result[name] = self._value
        self._value = result

    def visit_array(self, expr: ArrayTypeExpr) -> None:
        self._value = [self.build_for_type_expr(expr.items)]

    def visit_enum(self, expr: EnumTypeExpr) -> None:
        self._value = expr.values[0] if expr.values else None

    def visit_primitive(self, expr: PrimitiveTypeExpr) -> None:
        self._value = _example_for_primitive_format(expr.format)


def build_example(schema: Schema) -> dict[str, Any]:
    """Build example data for the whole schema."""
    return ExampleBuilder().build_for_schema(schema)
