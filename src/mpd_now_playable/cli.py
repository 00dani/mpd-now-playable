import asyncio
from os import environ

from corefoundationasyncio import CoreFoundationEventLoop

from .cocoa.now_playing import CocoaNowPlaying
from .mpd.listener import MpdStateListener


async def listen() -> None:
	port = int(environ.get("MPD_PORT", "6600"))
	host = environ.get("MPD_HOST", "localhost")
	password = environ.get("MPD_PASSWORD")
	cache = environ.get("MPD_NOW_PLAYABLE_CACHE")
	if password is None and "@" in host:
		password, host = host.split("@", maxsplit=1)

	listener = MpdStateListener(cache)
	now_playing = CocoaNowPlaying(listener)
	await listener.start(host=host, port=port, password=password)
	await listener.loop(now_playing)


def make_loop() -> CoreFoundationEventLoop:
	return CoreFoundationEventLoop(console_app=True)


def main() -> None:
	asyncio.run(listen(), loop_factory=make_loop, debug=True)


if __name__ == "__main__":
	main()
