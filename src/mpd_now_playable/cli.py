import asyncio
from collections.abc import Iterable

from rich import print

from .__version__ import __version__
from .config.load import loadConfig
from .config.model import Config
from .mpd.listener import MpdStateListener
from .song_receiver import (
	Receiver,
	choose_loop_factory,
	import_receiver,
)


async def listen(
	config: Config, listener: MpdStateListener, receiver_types: Iterable[type[Receiver]]
) -> None:
	await listener.start(config.mpd)
	receivers = (rec(listener, config) for rec in receiver_types)
	await listener.loop(receivers)


def main() -> None:
	print(f"mpd-now-playable v{__version__}")
	config = loadConfig()
	print(config)

	listener = MpdStateListener(config.cache)
	receiver_types = tuple(import_receiver(rec) for rec in config.receivers)

	factory = choose_loop_factory(receiver_types)
	asyncio.run(
		listen(config, listener, receiver_types),
		loop_factory=factory.make_loop,
		debug=True,
	)


if __name__ == "__main__":
	main()
