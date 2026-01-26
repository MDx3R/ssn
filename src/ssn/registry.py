"""Type registry for resolving type references."""

from __future__ import annotations

from ssn.ast import TypeDef
from ssn.exceptions import TypeNotFoundError


class TypeRegistry:
    """Registry for type definitions."""

    def __init__(self) -> None:
        """Initialize an empty type registry."""
        self._types: dict[str, TypeDef] = {}

    def register(self, type_def: TypeDef) -> None:
        """Register a type definition."""
        if type_def.name in self._types:
            raise ValueError(f"Type '{type_def.name}' is already registered")
        self._types[type_def.name] = type_def

    def get(self, name: str) -> TypeDef:
        """Get a type definition by name."""
        if name not in self._types:
            raise TypeNotFoundError(name)
        return self._types[name]

    def has(self, name: str) -> bool:
        """Check if a type is registered."""
        return name in self._types

    def register_all(self, *types: TypeDef) -> None:
        """Register multiple type definitions at once."""
        for type_def in types:
            self.register(type_def)
