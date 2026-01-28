from typing import Any, cast

from ssn.ast import (
    ArrayTypeExpr,
    EnumTypeExpr,
    NodeMeta,
    ObjectTypeExpr,
    PrimitiveTypeExpr,
    PropertyDef,
    Schema,
    TypeDef,
    TypeExpr,
    TypeRef,
)
from ssn.loader.types import (
    RawArrayType,
    RawEnumType,
    RawObjectType,
    RawPrimitiveType,
    RawPropertyDef,
    RawSchema,
    RawTypeDef,
    RawTypeRef,
)


def load_object_expr(raw: RawObjectType) -> ObjectTypeExpr:
    properties = {
        prop_name: load_property(prop_name, prop_raw)
        for prop_name, prop_raw in raw["properties"].items()
    }

    return ObjectTypeExpr(properties=properties)


def load_array_expr(raw: RawArrayType) -> ArrayTypeExpr:
    return ArrayTypeExpr(items=load_type_expr(raw["items"]))


def load_enum_expr(raw: RawEnumType) -> EnumTypeExpr:
    return EnumTypeExpr(values=raw["values"])


def load_primitive_expr(raw: RawPrimitiveType) -> PrimitiveTypeExpr:
    return PrimitiveTypeExpr(format=raw.get("format"))


def load_type_ref(raw: RawTypeRef) -> TypeRef:
    return TypeRef(raw["type"])


def load_type_expr(raw: RawTypeDef) -> TypeExpr:
    if isinstance(raw, str):
        return TypeRef(raw)

    match raw["type"]:
        case "object":
            return load_object_expr(raw)
        case "array":
            return load_array_expr(raw)
        case "enum":
            return load_enum_expr(raw)
        case _:
            return load_type_ref(raw)


def load_meta(raw: dict[str, Any] | None) -> NodeMeta | None:
    if raw is None:
        return None

    return NodeMeta(
        description=raw.get("description"),
        deprecated=bool(raw.get("deprecated", False)),
    )


def load_property(name: str, raw: RawPropertyDef) -> PropertyDef:
    if isinstance(raw, str):
        return PropertyDef(name=name, type=load_type_expr(cast(RawTypeDef, raw)))

    return PropertyDef(
        name=name,
        type=load_type_expr(cast(RawTypeDef, raw)),
        required=raw.get("required", True),
        nullable=raw.get("nullable", False),
        default=raw.get("default"),
        meta=load_meta(raw.get("meta")),
    )


def load_object_type(name: str, raw: RawObjectType) -> TypeDef:
    return TypeDef(
        name=name, expr=load_object_expr(raw), meta=load_meta(raw.get("meta"))
    )


def load_array_type(name: str, raw: RawArrayType) -> TypeDef:
    return TypeDef(
        name=name, expr=load_array_expr(raw), meta=load_meta(raw.get("meta"))
    )


def load_enum_type(name: str, raw: RawEnumType) -> TypeDef:
    return TypeDef(name=name, expr=load_enum_expr(raw), meta=load_meta(raw.get("meta")))


def load_primitive_type(name: str, raw: RawPrimitiveType) -> TypeDef:
    return TypeDef(
        name=name, expr=load_primitive_expr(raw), meta=load_meta(raw.get("meta"))
    )


def load_type(name: str, raw: RawTypeDef) -> TypeDef:
    if isinstance(raw, str):
        return TypeDef(name=name, expr=load_type_expr(raw))

    match raw["type"]:
        case "object":
            return load_object_type(name, raw)
        case "array":
            return load_array_type(name, raw)
        case "enum":
            return load_enum_type(name, raw)
        case _:
            return load_primitive_type(name, raw)


def load_schema(raw: RawSchema) -> Schema:
    raw_types = raw["definitions"]["types"]

    types: dict[str, TypeDef] = {
        name: load_type(name, type_raw) for name, type_raw in raw_types.items()
    }

    root = [load_property(name, type) for name, type in raw["schema"].items()]

    return Schema(version=raw["version"], types=types, root=root)
