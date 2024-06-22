from os import environ

from apischema import deserialize
from pytomlpp import load
from xdg_base_dirs import xdg_config_home

from .model import Config

__all__ = "loadConfig"


def loadConfigFromFile() -> Config:
	path = xdg_config_home() / "mpd-now-playable" / "config.toml"
	data = load(path)
	print(f"Loaded your configuration from {path}")
	return deserialize(Config, data)


def loadConfigFromEnv() -> Config:
	port = int(environ["MPD_PORT"]) if "MPD_PORT" in environ else None
	host = environ.get("MPD_HOST")
	password = environ.get("MPD_PASSWORD")
	cache = environ.get("MPD_NOW_PLAYABLE_CACHE")
	if password is None and host is not None and "@" in host:
		password, host = host.split("@", maxsplit=1)
	data = {"cache": cache, "mpd": {"port": port, "host": host, "password": password}}
	return deserialize(Config, data)


def loadConfig() -> Config:
	try:
		return loadConfigFromFile()
	except FileNotFoundError:
		return loadConfigFromEnv()
