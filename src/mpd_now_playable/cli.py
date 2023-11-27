import asyncio
from os import environ

from corefoundationasyncio import CoreFoundationEventLoop

from .cocoa import CocoaNowPlaying
from .mpd.listener import MpdStateListener


async def listen() -> None:
	listener = MpdStateListener()
	now_playing = CocoaNowPlaying(listener)
	await listener.start(
		hostname=environ.get("MPD_HOSTNAME", "localhost"),
		port=int(environ.get("MPD_PORT", "6600")),
		password=environ.get("MPD_PASSWORD"),
	)
	await listener.loop(now_playing)


def make_loop() -> CoreFoundationEventLoop:
	return CoreFoundationEventLoop(console_app=True)


def main() -> None:
	asyncio.run(listen(), loop_factory=make_loop, debug=True)


if __name__ == "__main__":
	main()
