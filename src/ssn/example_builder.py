from __future__ import annotations

from typing import Any

from ssn.ast import (
    ArrayTypeExpr,
    EnumTypeExpr,
    ObjectTypeExpr,
    PrimitiveType,
    PrimitiveTypeExpr,
    PropertyDef,
    Schema,
    TypeDef,
    TypeExpr,
    TypeRef,
)
from ssn.visitor import ExprVisitor


class ExampleBuilder(ExprVisitor):
    """Visitor that builds example data from Schema AST.

    High level rules:
    - use explicit `default` if present;
    - for enums use the first value;
    - for nullable properties, use `None` (even if default is missing);
    - for arrays, produce a single-element array with an example of the item type;
    - for objects, recursively build examples for properties;
    - for references, delegate to the referenced type definition.
    """

    def __init__(self) -> None:
        self._value: Any = None

    def build_for_schema(self, schema: Schema) -> dict[str, Any]:
        """Build example object for the root schema."""
        result: dict[str, Any] = {}
        for prop in schema.root:
            value = self.build_for_property(prop)
            # Skip completely missing optional values, but keep explicit None/defaults.
            if value is _MISSING:
                continue
            result[prop.name] = value
        return result

    def build_for_property(self, prop: PropertyDef) -> Any:
        # 1. Explicit default wins.
        if prop.default is not None:
            return prop.default

        # 2. Nullable but no default -> use None.
        if prop.nullable:
            return None

        # 3. Otherwise, derive from type expression.
        value = self.build_for_type_expr(prop.type)
        # For optional (required=False) properties, we might choose to skip them
        # entirely; callers can detect this via `_MISSING`.
        if prop.required:
            return value
        return value

    def build_for_type_expr(self, expr: TypeExpr) -> Any:
        expr.visit(self)
        return self._value

    def build_for_typedef(self, typedef: TypeDef | None) -> Any:
        if typedef is None:
            # Unresolved reference; return placeholder.
            return None
        # If this is a `PrimitiveType`, use its primitive expr directly.
        if isinstance(typedef, PrimitiveType):
            return self._build_primitive_from_typedef(typedef)
        return self.build_for_type_expr(typedef.expr)

    def _build_primitive_from_typedef(self, typedef: PrimitiveType) -> Any:
        expr = typedef.expr
        assert isinstance(expr, PrimitiveTypeExpr)
        # Reuse the same logic as in visit_primitive.
        fmt = expr.format
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

    # ExprVisitor implementation -------------------------------------------------

    def visit_ref(self, expr: TypeRef) -> None:
        self._value = self.build_for_typedef(expr.resolved)

    def visit_object(self, expr: ObjectTypeExpr) -> None:
        result: dict[str, Any] = {}
        for name, prop in expr.properties.items():
            value = self.build_for_property(prop)
            if value is _MISSING:
                continue
            result[name] = value
        self._value = result

    def visit_array(self, expr: ArrayTypeExpr) -> None:
        # Single representative element.
        self._value = [self.build_for_type_expr(expr.items)]

    def visit_enum(self, expr: EnumTypeExpr) -> None:
        self._value = expr.values[0] if expr.values else None

    def visit_primitive(self, expr: PrimitiveTypeExpr) -> None:
        fmt = expr.format
        # Very small set of well-known formats/aliases; can be extended later.
        if fmt in ("integer", "int"):
            self._value = 1
            return
        if fmt in ("number", "float", "double"):
            self._value = 1.0
            return
        if fmt in ("boolean", "bool"):
            self._value = True
            return
        if fmt in ("UUID", "uuid", "guid"):
            self._value = "00000000-0000-0000-0000-000000000000"
            return
        if fmt in ("json", "object"):
            self._value = {}
            return
        # Default: string placeholder, including when format is None.
        self._value = "string"


class _Missing:
    """Sentinel for 'no value' to distinguish from None/defaults."""


_MISSING = _Missing()


def build_example(schema: Schema) -> dict[str, Any]:
    """Build example data for the whole schema."""
    return ExampleBuilder().build_for_schema(schema)
