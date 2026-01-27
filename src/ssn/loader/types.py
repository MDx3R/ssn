from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class RawMeta(TypedDict):
    description: NotRequired[str]
    deprecated: NotRequired[bool]


class RawProperty(TypedDict):
    type: str
    required: NotRequired[bool]
    nullable: NotRequired[bool]
    default: NotRequired[object]
    meta: NotRequired[dict[str, object]]

    # NOTE: Type specific properties
    format: NotRequired[str]
    items: NotRequired[str]
    values: NotRequired[list[str]]
    properties: NotRequired[dict[str, RawProperty]]


class RawObjectType(TypedDict):
    type: Literal["object"]
    properties: dict[str, RawProperty]
    meta: NotRequired[dict[str, object]]


class RawArrayType(TypedDict):
    type: Literal["array"]
    items: RawTypeDef
    meta: NotRequired[dict[str, object]]


class RawEnumType(TypedDict):
    type: Literal["enum"]
    values: list[str]
    meta: NotRequired[dict[str, object]]


class RawPrimitiveType(TypedDict):
    type: Literal["primitive"]
    format: NotRequired[str]
    meta: NotRequired[dict[str, object]]


RawTypeRef = RawPrimitiveType
RawTypeDef = (
    RawObjectType | RawArrayType | RawEnumType | RawPrimitiveType | RawTypeRef | str
)


class RawSchema(TypedDict):
    version: str
    definitions: dict[str, dict[str, RawTypeDef]]
    schema: dict[str, RawTypeDef]
