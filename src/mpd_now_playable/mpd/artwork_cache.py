from __future__ import annotations

from yarl import URL

from ..cache import Cache, make_cache
from ..song import Artwork, ArtworkSchema, to_artwork
from ..tools.asyncio import run_background_task
from ..tools.types import un_maybe_plural
from .types import CurrentSongResponse, MpdStateHandler

CACHE_TTL = 60 * 60  # seconds = 1 hour


def calc_album_key(song: CurrentSongResponse) -> str:
	artist = sorted(
		un_maybe_plural(song.get("albumartist", song.get("artist", "Unknown Artist")))
	)
	album = sorted(un_maybe_plural(song.get("album", "Unknown Album")))
	return ":".join(";".join(t).replace(":", "-") for t in (artist, album))


def calc_track_key(song: CurrentSongResponse) -> str:
	return song["file"]


MEMORY = URL("memory://")


class MpdArtworkCache:
	mpd: MpdStateHandler
	album_cache: Cache[Artwork]
	track_cache: Cache[Artwork]
	pending_tracks: set[str]

	def __init__(self, mpd: MpdStateHandler, cache_url: URL = MEMORY):
		self.mpd = mpd
		self.album_cache = make_cache(ArtworkSchema, cache_url, "album")
		self.track_cache = make_cache(ArtworkSchema, cache_url, "track")
		self.pending_tracks = set()

	async def get_cached_artwork(self, song: CurrentSongResponse) -> bytes | None:
		track_key = calc_track_key(song)
		art = await self.track_cache.get(track_key)
		if art is not None:
			# NoArtwork is a valid cached value too: returning None here avoids
			# repeatedly re-querying MPD for files that have no embedded art.
			if art:
				return art.data
			return None

		# If we don't have track artwork cached, go find some.
		if track_key not in self.pending_tracks:
			self.pending_tracks.add(track_key)
			run_background_task(self.cache_artwork(song))

		# Even if we don't have cached track art, we can try looking for cached album art.
		art = await self.album_cache.get(calc_album_key(song))
		if art:
			return art.data

		return None

	async def cache_artwork(self, song: CurrentSongResponse) -> None:
		track_key = calc_track_key(song)
		try:
			art = to_artwork(await self.mpd.get_art(song["file"]))
			try:
				await self.album_cache.add(calc_album_key(song), art, ttl=CACHE_TTL)
			except ValueError:
				pass
			await self.track_cache.set(track_key, art, ttl=CACHE_TTL)
			# Refresh receivers only when we discovered actual artwork.
			if art:
				await self.mpd.refresh()
		finally:
			self.pending_tracks.discard(track_key)
