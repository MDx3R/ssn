"""AST model for DSL schema representation."""

from __future__ import annotations

from abc import ABC, abstractmethod
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any


if TYPE_CHECKING:
    from ssn.registry import TypeRegistry
    from ssn.visitor import ExprVisitor


@dataclass(slots=True)
class NodeMeta:
    """Metadata for AST nodes."""

    description: Any | None = None
    deprecated: bool = False
    # Can be extended with example, doc, etc.


@dataclass(slots=True, kw_only=True)
class ASTNode:
    """Base class for all AST nodes."""

    meta: NodeMeta | None = field(default=None)


class TypeExpr(ABC):
    @abstractmethod
    def resolve(self, registry: TypeRegistry) -> None: ...
    @abstractmethod
    def visit(self, visior: ExprVisitor) -> None: ...


@dataclass(slots=True)
class PrimitiveTypeExpr(TypeExpr):
    """Primitive type definition (string, integer, number, boolean, etc.)."""

    format: str | None = None

    def resolve(self, registry: TypeRegistry) -> None:
        pass

    def visit(self, visior: ExprVisitor) -> None:
        visior.visit_primitive(self)


@dataclass(slots=True)
class EnumTypeExpr(TypeExpr):
    """Enum type definition."""

    values: Sequence[str]

    def resolve(self, registry: TypeRegistry) -> None:
        pass

    def visit(self, visior: ExprVisitor) -> None:
        visior.visit_enum(self)


@dataclass(slots=True)
class ArrayTypeExpr(TypeExpr):
    """Array type definition."""

    items: TypeExpr

    def resolve(self, registry: TypeRegistry) -> None:
        self.items.resolve(registry)

    def visit(self, visior: ExprVisitor) -> None:
        visior.visit_array(self)


@dataclass(slots=True)
class ObjectTypeExpr(TypeExpr):
    """Object type definition."""

    properties: Mapping[str, PropertyDef]

    def resolve(self, registry: TypeRegistry) -> None:
        for prop in self.properties.values():
            prop.type.resolve(registry)

    def visit(self, visior: ExprVisitor) -> None:
        visior.visit_object(self)


@dataclass(slots=True)
class TypeDef(ASTNode):
    """Base class for all type definitions."""

    name: str
    expr: TypeExpr


@dataclass(slots=True)
class PrimitiveType(TypeDef):
    """Primitive type definition (string, integer, number, boolean, etc.)."""

    expr: TypeExpr = field(default_factory=PrimitiveTypeExpr)


@dataclass(slots=True)
class PropertyDef(ASTNode):
    """Property definition within an object type."""

    name: str
    type: TypeExpr
    required: bool = True
    nullable: bool = False
    default: object | None = None


@dataclass(slots=True)
class TypeRef(TypeExpr):
    """Reference to a type definition."""

    name: str
    resolved: TypeDef | None = field(default=None, init=False)

    def resolve(self, registry: TypeRegistry) -> None:
        """Resolve this reference using the provided registry."""
        if self.resolved is not None:
            return
        self.resolved = registry.get(self.name)

    def visit(self, visior: ExprVisitor) -> None:
        visior.visit_ref(self)


@dataclass(slots=True)
class Schema(ASTNode):
    """Root schema AST node."""

    version: str
    types: Mapping[str, TypeDef]
    root: Sequence[PropertyDef]
