from typing import Annotated, NewType

from annotated_types import Ge, Le
from pydantic import (
	Field,
	PlainSerializer,
	PlainValidator,
	SecretStr,
	Strict,
	WithJsonSchema,
)
from yarl import URL as Yarl

__all__ = ("Host", "Password", "Port", "Url")


def from_yarl(url: Yarl) -> str:
	return url.human_repr()


def to_yarl(value: object) -> Yarl:
	if isinstance(value, str):
		return Yarl(value)
	raise NotImplementedError(f"Cannot convert {type(object)} to URL")


Host = NewType(
	"Host", Annotated[str, Strict(), Field(json_schema_extra={"format": "hostname"})]
)
Password = NewType("Password", Annotated[SecretStr, Strict()])
Port = NewType("Port", Annotated[int, Strict(), Ge(1), Le(65535)])
Url = Annotated[
	Yarl,
	PlainValidator(to_yarl),
	PlainSerializer(from_yarl, return_type=str),
	WithJsonSchema({"type": "string", "format": "uri"}),
]
