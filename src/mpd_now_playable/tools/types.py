from typing import Callable, TypeVar

__all__ = ("convert_if_exists",)

T = TypeVar("T")


def convert_if_exists(value: str | None, converter: Callable[[str], T]) -> T | None:
	if value is None:
		return None
	return converter(value)
