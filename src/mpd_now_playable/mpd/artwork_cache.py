from aiocache import Cache

from ..async_tools import run_background_task
from .types import CurrentSongResponse, MpdStateHandler

CACHE_TTL = 60 * 10  # ten minutes


def calc_album_key(song: CurrentSongResponse) -> str:
	return f'{song["albumartist"]}:-:-:{song["album"]}'


def calc_track_key(song: CurrentSongResponse) -> str:
	return song["file"]


class MpdArtworkCache:
	mpd: MpdStateHandler
	album_cache: 'Cache[bytes | None]'
	track_cache: 'Cache[bytes | None]'

	def __init__(self, mpd: MpdStateHandler):
		self.mpd = mpd
		self.album_cache = Cache()
		self.track_cache = Cache()

	async def get_cached_artwork(self, song: CurrentSongResponse) -> bytes | None:
		art = await self.track_cache.get(calc_track_key(song))
		if art:
			return art

		# If we don't have track artwork cached, go find some.
		run_background_task(self.cache_artwork(song))

		# Even if we don't have cached track art, we can try looking for cached album art.
		art = await self.album_cache.get(calc_album_key(song))
		if art:
			return art

		return None

	async def cache_artwork(self, song: CurrentSongResponse) -> None:
		art = await self.mpd.readpicture(song["file"])
		try:
			await self.album_cache.add(calc_album_key(song), art, ttl=CACHE_TTL)
		except ValueError:
			pass
		await self.track_cache.set(calc_track_key(song), art, ttl=CACHE_TTL)
		await self.mpd.refresh()
