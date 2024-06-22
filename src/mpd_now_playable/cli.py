import asyncio

from corefoundationasyncio import CoreFoundationEventLoop

from .__version__ import __version__
from .cocoa.now_playing import CocoaNowPlaying
from .config.load import loadConfig
from .mpd.listener import MpdStateListener


async def listen() -> None:
	print(f"mpd-now-playable v{__version__}")
	config = loadConfig()
	listener = MpdStateListener(config.cache)
	now_playing = CocoaNowPlaying(listener)
	await listener.start(config.mpd)
	await listener.loop(now_playing)


def make_loop() -> CoreFoundationEventLoop:
	return CoreFoundationEventLoop(console_app=True)


def main() -> None:
	asyncio.run(listen(), loop_factory=make_loop, debug=True)


if __name__ == "__main__":
	main()
