from pathlib import Path

from yarl import URL

from ...config.model import MpdConfig
from ...playback.state import PlaybackState
from ...song import Song, Stopped, to_artwork, to_brainz
from ...tools.types import option_fmap, un_maybe_plural
from ..types import MpdState


def file_to_url(config: MpdConfig, file: str) -> URL | None:
	url = URL(file)
	if url.scheme != "":
		# We already got an absolute URL - probably a stream? - so we can just return it.
		return url

	if not config.music_directory:
		# We have a relative song URI, but we can't make it absolute since no music directory is configured.
		return None

	# Prepend the configured music directory, then turn the whole path into a file:// URL.
	abs_file = config.music_directory / file
	return URL(abs_file.as_uri())


def to_song(config: MpdConfig, mpd: MpdState) -> Song | Stopped:
	state = PlaybackState(mpd.status["state"])
	if state == PlaybackState.stop:
		return Stopped()

	file = mpd.current["file"]
	url = file_to_url(config, file)

	return Song(
		state=state,
		file=Path(file),
		url=url,
		title=mpd.current.get("title"),
		artist=un_maybe_plural(mpd.current.get("artist")),
		album=un_maybe_plural(mpd.current.get("album")),
		album_artist=un_maybe_plural(mpd.current.get("albumartist")),
		composer=un_maybe_plural(mpd.current.get("composer")),
		genre=un_maybe_plural(mpd.current.get("genre")),
		track=option_fmap(int, mpd.current.get("track")),
		disc=option_fmap(int, mpd.current.get("disc")),
		duration=option_fmap(float, mpd.status.get("duration")),
		elapsed=float(mpd.status["elapsed"]),
		musicbrainz=to_brainz(mpd.current),
		art=to_artwork(mpd.art),
	)
