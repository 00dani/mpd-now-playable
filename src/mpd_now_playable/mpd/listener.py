import asyncio
from collections.abc import Iterable

from mpd.asyncio import MPDClient
from mpd.base import CommandError
from rich import print as rprint
from yarl import URL

from ..config.model import MpdConfig
from ..playback import Playback
from ..playback.state import PlaybackState
from ..player import Player
from ..song_receiver import Receiver
from ..tools.asyncio import run_background_task
from .artwork_cache import MpdArtworkCache
from .convert.to_playback import to_playback
from .types import MpdState


class MpdStateListener(Player):
	config: MpdConfig
	client: MPDClient
	receivers: Iterable[Receiver]
	art_cache: MpdArtworkCache
	idle_count = 0

	def __init__(self, cache: URL | None = None) -> None:
		self.client = MPDClient()
		self.art_cache = (
			MpdArtworkCache(self, cache) if cache else MpdArtworkCache(self)
		)

	async def start(self, conf: MpdConfig) -> None:
		self.config = conf
		print(f"Connecting to MPD server {conf.host}:{conf.port}...")
		await self.client.connect(conf.host, conf.port)
		if conf.password is not None:
			print("Authorising to MPD with your password...")
			await self.client.password(conf.password.get_secret_value())
		print(f"Connected to MPD v{self.client.mpd_version}")
		run_background_task(self.heartbeat())

	async def heartbeat(self) -> None:
		while True:
			await self.client.ping()
			await asyncio.sleep(10)

	async def refresh(self) -> None:
		await self.update_receivers()

	async def loop(self, receivers: Iterable[Receiver]) -> None:
		self.receivers = receivers
		# Notify our receivers of the initial state MPD is in when this script loads up.
		await self.update_receivers()
		# And then wait for stuff to change in MPD. :)
		async for subsystems in self.client.idle():
			# If no subsystems actually changed, we don't need to update the receivers.
			if not subsystems:
				continue
			self.idle_count += 1
			await self.update_receivers()

	async def update_receivers(self) -> None:
		# If any async calls in here take long enough that we got another MPD idle event, we want to bail out of this older update.
		starting_idle_count = self.idle_count
		status, current = await asyncio.gather(
			self.client.status(), self.client.currentsong()
		)
		state = MpdState(status, current)

		if starting_idle_count != self.idle_count:
			return

		art = None
		if status["state"] != "stop":
			art = await self.art_cache.get_cached_artwork(current)
			if starting_idle_count != self.idle_count:
				return

		state = MpdState(status, current, art)
		pb = to_playback(self.config, state)
		rprint(pb)
		await self.update(pb)

	async def update(self, playback: Playback) -> None:
		await asyncio.gather(*(r.update(playback) for r in self.receivers))

	async def get_art(self, file: str) -> bytes | None:
		picture = await self.readpicture(file)
		if picture:
			return picture
		return await self.albumart(file)

	async def albumart(self, file: str) -> bytes | None:
		try:
			albumart = await self.client.albumart(file)
			return albumart.get("binary")
		except CommandError:
			return None

	async def readpicture(self, file: str) -> bytes | None:
		try:
			readpic = await self.client.readpicture(file)
			return readpic.get("binary")
		except CommandError:
			return None

	async def on_play_pause(self) -> PlaybackState:
		# python-mpd2 has direct support for toggling the play/pause state by
		# calling MPDClient.pause(None), but it doesn't tell you the final
		# state, and we also want to support playing from stopped, so we need
		# to handle this ourselves.
		status = await self.client.status()
		return await {
			"play": self.on_pause,
			"pause": self.on_play,
			"stop": self.on_play,
		}[status["state"]]()

	async def on_play(self) -> PlaybackState:
		await self.client.play()
		return PlaybackState.play

	async def on_pause(self) -> PlaybackState:
		await self.client.pause(1)
		return PlaybackState.pause

	async def on_stop(self) -> PlaybackState:
		await self.client.stop()
		return PlaybackState.stop

	async def on_next(self) -> None:
		await self.client.next()

	async def on_prev(self) -> None:
		await self.client.previous()

	async def on_seek(self, position: float) -> None:
		await self.client.seekcur(position)
