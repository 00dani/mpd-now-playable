import asyncio
import sys
from collections.abc import Iterable

from rich import print

from .__version__ import __version__
from .config.load import loadConfig
from .config.model import Config
from .mpd.listener import MpdStateListener
from .song_receiver import (
	Receiver,
	choose_loop_factory,
	construct_receiver,
)


async def listen(
	config: Config, listener: MpdStateListener, receivers: Iterable[Receiver]
) -> None:
	await listener.start(config.mpd)
	await asyncio.gather(*(rec.start(listener) for rec in receivers))
	await listener.loop(receivers)


def print_help() -> None:
	print("Usage: mpd-now-playable [OPTIONS]")
	print("")
	print("Options:")
	print("  -h, --help     Show this help message and exit.")
	print("  -v, --version  Show version and exit.")


def main() -> None:
	args = set(sys.argv[1:])
	if "-h" in args or "--help" in args:
		print_help()
		return
	if "-v" in args or "--version" in args:
		print(f"mpd-now-playable v{__version__}")
		return

	print(f"mpd-now-playable v{__version__}")
	config = loadConfig()
	print(config)

	listener = MpdStateListener(config.cache)
	receivers = tuple(construct_receiver(rec_config) for rec_config in config.receivers)
	factory = choose_loop_factory(receivers)

	asyncio.run(
		listen(config, listener, receivers),
		loop_factory=factory.make_loop,
		debug=False,
	)


if __name__ == "__main__":
	main()
