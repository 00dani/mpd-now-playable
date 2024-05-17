import asyncio
from pathlib import Path
from uuid import UUID

from mpd.asyncio import MPDClient
from mpd.base import CommandError

from ..player import Player
from ..song import PlaybackState, Song, SongListener
from ..type_tools import convert_if_exists
from .artwork_cache import MpdArtworkCache
from .types import CurrentSongResponse, StatusResponse


def mpd_current_to_song(
	status: StatusResponse, current: CurrentSongResponse, art: bytes | None
) -> Song:
	return Song(
		state=PlaybackState(status["state"]),
		queue_index=int(current["pos"]),
		queue_length=int(status["playlistlength"]),
		file=Path(current["file"]),
		musicbrainz_trackid=convert_if_exists(current.get("musicbrainz_trackid"), UUID),
		musicbrainz_releasetrackid=convert_if_exists(
			current.get("musicbrainz_releasetrackid"), UUID
		),
		title=current.get("title"),
		artist=current.get("artist"),
		album=current.get("album"),
		album_artist=current.get("albumartist"),
		composer=current.get("composer"),
		genre=current.get("genre"),
		track=convert_if_exists(current.get("track"), int),
		disc=convert_if_exists(current.get("disc"), int),
		duration=float(status["duration"]),
		elapsed=float(status["elapsed"]),
		art=art,
	)


class MpdStateListener(Player):
	client: MPDClient
	listener: SongListener
	art_cache: MpdArtworkCache
	idle_count = 0

	def __init__(self, cache: str | None = None) -> None:
		self.client = MPDClient()
		self.art_cache = (
			MpdArtworkCache(self, cache) if cache else MpdArtworkCache(self)
		)

	async def start(
		self, host: str = "localhost", port: int = 6600, password: str | None = None
	) -> None:
		print(f"Connecting to MPD server {host}:{port}...")
		await self.client.connect(host, port)
		if password is not None:
			print("Authorising to MPD with your password...")
			await self.client.password(password)
		print(f"Connected to MPD v{self.client.mpd_version}")

	async def refresh(self) -> None:
		await self.update_listener(self.listener)

	async def loop(self, listener: SongListener) -> None:
		self.listener = listener
		# notify our listener of the initial state MPD is in when this script loads up.
		await self.update_listener(listener)
		# then wait for stuff to change in MPD. :)
		async for _ in self.client.idle():
			self.idle_count += 1
			await self.update_listener(listener)

	async def update_listener(self, listener: SongListener) -> None:
		# If any async calls in here take long enough that we got another MPD idle event, we want to bail out of this older update.
		starting_idle_count = self.idle_count
		status, current = await asyncio.gather(
			self.client.status(), self.client.currentsong()
		)

		if starting_idle_count != self.idle_count:
			return

		if status["state"] == "stop":
			print("Nothing playing")
			listener.update(None)
			return

		art = await self.art_cache.get_cached_artwork(current)
		if starting_idle_count != self.idle_count:
			return

		song = mpd_current_to_song(status, current, art)
		print(song)
		listener.update(song)

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
