from dataclasses import field
from typing import NewType, Optional, TypeVar

from apischema import schema
from apischema.conversions import deserializer
from apischema.metadata import none_as_undefined
from yarl import URL

__all__ = ("Host", "Port", "optional")

T = TypeVar("T")

Host = NewType("Host", str)
schema(format="hostname")(Host)

Port = NewType("Port", int)
schema(min=1, max=65535)(Port)

schema(format="uri")(URL)


def optional() -> Optional[T]:
	return field(default=None, metadata=none_as_undefined)


@deserializer
def from_yarl(url: str) -> URL:
	return URL(url)
