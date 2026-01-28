from abc import ABC, abstractmethod

from ssn.ast import (
    ArrayTypeExpr,
    EnumTypeExpr,
    ObjectTypeExpr,
    PrimitiveTypeExpr,
    TypeRef,
)


class ExprVisitor(ABC):
    @abstractmethod
    def visit_ref(self, expr: TypeRef) -> None: ...
    @abstractmethod
    def visit_object(self, expr: ObjectTypeExpr) -> None: ...
    @abstractmethod
    def visit_array(self, expr: ArrayTypeExpr) -> None: ...
    @abstractmethod
    def visit_enum(self, expr: EnumTypeExpr) -> None: ...
    @abstractmethod
    def visit_primitive(self, expr: PrimitiveTypeExpr) -> None: ...
