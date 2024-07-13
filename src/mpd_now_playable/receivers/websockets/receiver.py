from pathlib import Path

import ormsgpack
from websockets import broadcast
from websockets.server import WebSocketServerProtocol, serve

from ...config.model import WebsocketsReceiverConfig
from ...player import Player
from ...song import Song
from ...song_receiver import DefaultLoopFactory, Receiver

MSGPACK_NULL = ormsgpack.packb(None)


def default(value: object) -> object:
	if isinstance(value, Path):
		return str(value)
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
		await serve(self.handle, host=self.config.host, port=self.config.port)

	async def handle(self, conn: WebSocketServerProtocol) -> None:
		self.connections.add(conn)
		await conn.send(self.last_status)
		try:
			await conn.wait_closed()
		finally:
			self.connections.remove(conn)

	async def update(self, song: Song | None) -> None:
		if song is None:
			self.last_status = MSGPACK_NULL
		else:
			self.last_status = ormsgpack.packb(song, default=default)
		broadcast(self.connections, self.last_status)
