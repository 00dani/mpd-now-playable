from pathlib import Path

import ormsgpack
from websockets import broadcast
from websockets.asyncio.server import Server, ServerConnection, serve
from yarl import URL

from ...config.model import WebsocketsReceiverConfig
from ...playback import Playback
from ...player import Player
from ...song_receiver import DefaultLoopFactory, Receiver

MSGPACK_NULL = ormsgpack.packb(None)


def default(value: object) -> object:
	if isinstance(value, Path):
		return str(value)
	if isinstance(value, URL):
		return value.human_repr()
	raise TypeError


class WebsocketsReceiver(Receiver):
	config: WebsocketsReceiverConfig
	player: Player
	server: Server
	last_status: bytes = MSGPACK_NULL

	def __init__(self, config: WebsocketsReceiverConfig):
		self.config = config

	@classmethod
	def loop_factory(cls) -> DefaultLoopFactory:
		return DefaultLoopFactory()

	async def start(self, player: Player) -> None:
		self.player = player
		self.server = await serve(
			self.handle, host=self.config.host, port=self.config.port, reuse_port=True
		)

	async def handle(self, conn: ServerConnection) -> None:
		await conn.send(self.last_status)
		await conn.wait_closed()

	async def update(self, playback: Playback) -> None:
		self.last_status = ormsgpack.packb(playback, default=default)
		broadcast(self.server.connections, self.last_status)
