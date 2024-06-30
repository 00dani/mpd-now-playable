from collections.abc import Mapping
from os import environ
from typing import TypeVar

from boltons.iterutils import remap
from pytomlpp import load
from xdg_base_dirs import xdg_config_home

from .model import Config

__all__ = ("loadConfig",)
K = TypeVar("K")
V = TypeVar("V")


# Sadly this is the kind of function that's incredibly easy to type statically
# in something like TypeScript, but apparently impossible to type statically in
# Python. Basically the TypeScript typing looks like this:
#   type OmitNulls<T> = {[K in keyof T]?: OmitNulls<NonNullable<T[K]>>};
#   function withoutNulls<T>(data: T): OmitNulls<T>;
# But the Python type system (currently?) lacks mapped and index types, so you
# can't recurse over an arbitrary type's structure as OmitNulls<T> does, as
# well as conditional types so you can't easily define a "filtering" utility
# type like NonNullable<T>. Python's type system also doesn't infer a
# dictionary literal as having a structural type by default in the way
# TypeScript does, of course, so that part wouldn't work anyway.
def withoutNones(data: Mapping[K, V | None]) -> Mapping[K, V]:
	return remap(data, lambda p, k, v: v is not None)


def loadConfigFromFile() -> Config:
	path = xdg_config_home() / "mpd-now-playable" / "config.toml"
	data = load(path)
	print(f"Loaded your configuration from {path}")
	return Config.schema.validate_python(data)


def loadConfigFromEnv() -> Config:
	port = int(environ.pop("MPD_PORT")) if "MPD_PORT" in environ else None
	host = environ.pop("MPD_HOST", None)
	password = environ.pop("MPD_PASSWORD", None)
	cache = environ.pop("MPD_NOW_PLAYABLE_CACHE", None)
	if password is None and host is not None and "@" in host:
		password, host = host.split("@", maxsplit=1)
	data = {"cache": cache, "mpd": {"port": port, "host": host, "password": password}}
	return Config.schema.validate_python(withoutNones(data))


def loadConfig() -> Config:
	try:
		return loadConfigFromFile()
	except FileNotFoundError:
		return loadConfigFromEnv()
