from collections.abc import Callable, Mapping
from typing import TypeVar

# Apparently you need Python 3.13 for type var defaults to work. But since this
# is just a stub file, it's okay if they aren't supported at runtime.
KIn = TypeVar("KIn")
KOut = TypeVar("KOut", default=KIn)
VIn = TypeVar("VIn")
VOut = TypeVar("VOut", default=VIn)

type Path[KIn] = tuple[KIn, ...]

# remap() is Complicated and really difficult to define a type for, so I'm not
# surprised the boltons package doesn't try to type it for you. This particular
# type declaration works fine for my use of the function, but it's actually
# vastly more flexible than that - it'll accept any iterable as the root, not
# just mappings, and you can provide "enter" and "exit" callables to support
# arbitrary data structures.
def remap(
	root: Mapping[KIn, VIn],
	visit: Callable[[Path[KIn], KIn, VIn], tuple[KOut, VOut] | bool],
	reraise_visit: bool = False,
) -> Mapping[KOut, VOut]: ...
