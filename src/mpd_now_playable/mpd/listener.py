import asyncio
from collections.abc import Iterable
from pathlib import Path

from mpd.asyncio import MPDClient
from mpd.base import CommandError
from rich import print as rprint
from yarl import URL

from ..config.model import MpdConfig
from ..player import Player
from ..song import Artwork, PlaybackState, Song, to_artwork, to_brainz
from ..song_receiver import Receiver
from ..tools.types import convert_if_exists, un_maybe_plural
from .artwork_cache import MpdArtworkCache
from .types import CurrentSongResponse, StatusResponse


def mpd_current_to_song(
	status: StatusResponse, current: CurrentSongResponse, art: Artwork
) -> Song:
	return Song(
		state=PlaybackState(status["state"]),
		queue_index=int(current["pos"]),
		queue_length=int(status["playlistlength"]),
		file=Path(current["file"]),
		title=current.get("title"),
		artist=un_maybe_plural(current.get("artist")),
		album=un_maybe_plural(current.get("album")),
		album_artist=un_maybe_plural(current.get("albumartist")),
		composer=un_maybe_plural(current.get("composer")),
		genre=un_maybe_plural(current.get("genre")),
		track=convert_if_exists(current.get("track"), int),
		disc=convert_if_exists(current.get("disc"), int),
		duration=float(status["duration"]),
		elapsed=float(status["elapsed"]),
		musicbrainz=to_brainz(current),
		art=art,
	)


class MpdStateListener(Player):
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
		print(f"Connecting to MPD server {conf.host}:{conf.port}...")
		await self.client.connect(conf.host, conf.port)
		if conf.password is not None:
			print("Authorising to MPD with your password...")
			await self.client.password(conf.password.get_secret_value())
		print(f"Connected to MPD v{self.client.mpd_version}")

	async def refresh(self) -> None:
		await self.update_receivers()

	async def loop(self, receivers: Iterable[Receiver]) -> None:
		self.receivers = receivers
		# notify our receivers of the initial state MPD is in when this script loads up.
		await self.update_receivers()
		# then wait for stuff to change in MPD. :)
		async for _ in self.client.idle():
			self.idle_count += 1
			await self.update_receivers()

	async def update_receivers(self) -> None:
		# If any async calls in here take long enough that we got another MPD idle event, we want to bail out of this older update.
		starting_idle_count = self.idle_count
		status, current = await asyncio.gather(
			self.client.status(), self.client.currentsong()
		)

		if starting_idle_count != self.idle_count:
			return

		if status["state"] == "stop":
			print("Nothing playing")
			await self.update(None)
			return

		art = await self.art_cache.get_cached_artwork(current)
		if starting_idle_count != self.idle_count:
			return

		song = mpd_current_to_song(status, current, to_artwork(art))
		rprint(song)
		await self.update(song)

	async def update(self, song: Song | None) -> None:
		await asyncio.gather(*(r.update(song) for r in self.receivers))

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
