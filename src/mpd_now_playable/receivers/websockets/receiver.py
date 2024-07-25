from pathlib import Path

import ormsgpack
from websockets import broadcast
from websockets.server import WebSocketServerProtocol, serve
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
	connections: set[WebSocketServerProtocol]
	last_status: bytes = MSGPACK_NULL

	def __init__(self, config: WebsocketsReceiverConfig):
		self.config = config
		self.connections = set()

	@classmethod
	def loop_factory(cls) -> DefaultLoopFactory:
		return DefaultLoopFactory()

	async def start(self, player: Player) -> None:
		self.player = player
		await serve(
			self.handle, host=self.config.host, port=self.config.port, reuse_port=True
		)

	async def handle(self, conn: WebSocketServerProtocol) -> None:
		self.connections.add(conn)
		await conn.send(self.last_status)
		try:
			await conn.wait_closed()
		finally:
			self.connections.remove(conn)

	async def update(self, playback: Playback) -> None:
		self.last_status = ormsgpack.packb(playback, default=default)
		broadcast(self.connections, self.last_status)
