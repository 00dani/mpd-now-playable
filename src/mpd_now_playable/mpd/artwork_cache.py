from __future__ import annotations

from typing import TypedDict

from ..async_tools import run_background_task
from ..cache import Cache, make_cache
from .types import CurrentSongResponse, MpdStateHandler

CACHE_TTL = 60 * 60  # seconds = 1 hour


class ArtCacheEntry(TypedDict):
	data: bytes | None


def calc_album_key(song: CurrentSongResponse) -> str:
	artist = song.get("albumartist", song.get("artist", "Unknown Artist"))
	album = song.get("album", "Unknown Album")
	return ":".join(t.replace(":", "-") for t in (artist, album))


def calc_track_key(song: CurrentSongResponse) -> str:
	return song["file"]


class MpdArtworkCache:
	mpd: MpdStateHandler
	album_cache: Cache[ArtCacheEntry]
	track_cache: Cache[ArtCacheEntry]

	def __init__(self, mpd: MpdStateHandler, cache_url: str = "memory://"):
		self.mpd = mpd
		self.album_cache = make_cache(cache_url, "album")
		self.track_cache = make_cache(cache_url, "track")

	async def get_cached_artwork(self, song: CurrentSongResponse) -> bytes | None:
		art = await self.track_cache.get(calc_track_key(song))
		if art:
			return art["data"]

		# If we don't have track artwork cached, go find some.
		run_background_task(self.cache_artwork(song))

		# Even if we don't have cached track art, we can try looking for cached album art.
		art = await self.album_cache.get(calc_album_key(song))
		if art:
			return art["data"]

		return None

	async def cache_artwork(self, song: CurrentSongResponse) -> None:
		art = ArtCacheEntry(data=await self.mpd.get_art(song["file"]))
		try:
			await self.album_cache.add(calc_album_key(song), art, ttl=CACHE_TTL)
		except ValueError:
			pass
		await self.track_cache.set(calc_track_key(song), art, ttl=CACHE_TTL)
		await self.mpd.refresh()
