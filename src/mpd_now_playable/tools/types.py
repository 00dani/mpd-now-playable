from collections.abc import Callable
from typing import Any, TypeAlias, TypeVar

__all__ = (
	"AnyExceptList",
	"MaybePlural",
	"option_fmap",
	"convert_if_exists",
	"un_maybe_plural",
)

# Accept as many types as possible that are not lists. Yes, having to identify
# them manually like this is kind of a pain! TypeScript can express this
# restriction using a conditional type, and with another conditional type it
# can correctly type a version of un_maybe_plural that *does* accept lists, but
# Python's type system isn't quite that bonkers powerful. Yet?
AnyExceptList = (
	int
	| float
	| complex
	| bool
	| str
	| bytes
	| set[Any]
	| dict[Any, Any]
	| tuple[Any, ...]
	| Callable[[Any], Any]
	| type
)


U = TypeVar("U")
V = TypeVar("V")


def not_none(value: U | None) -> U:
	if value is None:
		raise ValueError("None should not be possible here.")
	return value


def option_fmap(f: Callable[[U], V], value: U | None) -> V | None:
	if value is None:
		return None
	return f(value)


def convert_if_exists(value: str | None, converter: Callable[[str], U]) -> U | None:
	if value is None:
		return None
	return converter(value)


T = TypeVar("T", bound=AnyExceptList)
MaybePlural: TypeAlias = list[T] | T


def un_maybe_plural(value: MaybePlural[T] | None) -> list[T]:
	match value:
		case None:
			return []
		case list(values):
			return values[:]
		case item:
			return [item]
