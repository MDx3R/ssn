from ssn.ast import Schema
from ssn.registry import TypeRegistry


def resolve_schema(schema: Schema, registry: TypeRegistry) -> None:
    for type_def in schema.types.values():
        registry.register(type_def)

    for t in schema.types.values():
        t.expr.resolve(registry)

    for ref in schema.root:
        ref.type.resolve(registry)
