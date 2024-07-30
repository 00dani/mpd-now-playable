from collections.abc import Callable
from typing import Any

__all__ = (
	"AnyExceptList",
	"MaybePlural",
	"option_fmap",
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


def not_none[U](value: U | None) -> U:
	if value is None:
		raise ValueError("None should not be possible here.")
	return value


def option_fmap[U, V](f: Callable[[U], V], value: U | None) -> V | None:
	if value is None:
		return None
	return f(value)


type MaybePlural[T: AnyExceptList] = list[T] | T


def un_maybe_plural[T: AnyExceptList](value: MaybePlural[T] | None) -> list[T]:
	match value:
		case None:
			return []
		case list(values):
			return values[:]
		case item:
			return [item]
