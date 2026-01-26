"""Custom exceptions for DSL parser."""

from __future__ import annotations


class DSLParserError(Exception):
    """Base exception for all DSL parser errors."""

    pass


class SchemaValidationError(DSLParserError):
    """Raised when schema structure is invalid."""

    def __init__(self, message: str, path: str | None = None) -> None:
        super().__init__(message)
        self.path = path
        self.message = message

    def __str__(self) -> str:
        if self.path:
            return f"{self.message} (at {self.path})"
        return self.message


class TypeNotFoundError(DSLParserError):
    """Raised when a type reference cannot be resolved."""

    def __init__(self, type_name: str, context: str | None = None) -> None:
        message = f"Type '{type_name}' not found"
        if context:
            message += f" in {context}"
        super().__init__(message)
        self.type_name = type_name
        self.context = context


class ReferenceResolutionError(DSLParserError):
    """Raised when a $ref cannot be resolved."""

    def __init__(self, ref: str, reason: str | None = None) -> None:
        message = f"Cannot resolve reference '{ref}'"
        if reason:
            message += f": {reason}"
        super().__init__(message)
        self.ref = ref
        self.reason = reason


class InvalidTypeDefinitionError(DSLParserError):
    """Raised when a type definition is invalid."""

    def __init__(self, type_name: str, message: str) -> None:
        super().__init__(f"Invalid type definition for '{type_name}': {message}")
        self.type_name = type_name
        self.message = message
