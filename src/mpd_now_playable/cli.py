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
	construct_receiver,
)


async def listen(
	config: Config, listener: MpdStateListener, receivers: Iterable[Receiver]
) -> None:
	await listener.start(config.mpd)
	await asyncio.gather(*(rec.start(listener) for rec in receivers))
	await listener.loop(receivers)


def main() -> None:
	print(f"mpd-now-playable v{__version__}")
	config = loadConfig()
	print(config)

	listener = MpdStateListener(config.cache)
	receivers = tuple(construct_receiver(rec_config) for rec_config in config.receivers)
	factory = choose_loop_factory(receivers)

	asyncio.run(
		listen(config, listener, receivers),
		loop_factory=factory.make_loop,
		debug=True,
	)


if __name__ == "__main__":
	main()
