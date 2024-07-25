from Foundation import NSMutableDictionary
from MediaPlayer import (
	MPMediaItemPropertyAlbumTitle,
	MPMediaItemPropertyAlbumTrackNumber,
	MPMediaItemPropertyArtist,
	MPMediaItemPropertyArtwork,
	MPMediaItemPropertyComposer,
	MPMediaItemPropertyDiscNumber,
	MPMediaItemPropertyGenre,
	MPMediaItemPropertyPersistentID,
	MPMediaItemPropertyPlaybackDuration,
	MPMediaItemPropertyTitle,
	MPNowPlayingInfoMediaTypeAudio,
	MPNowPlayingInfoPropertyAssetURL,
	MPNowPlayingInfoPropertyElapsedPlaybackTime,
	MPNowPlayingInfoPropertyExternalContentIdentifier,
	MPNowPlayingInfoPropertyMediaType,
	MPNowPlayingInfoPropertyPlaybackRate,
)

from ....playback.state import PlaybackState
from ....song import Song
from ..persistent_id import song_to_persistent_id
from .to_nsimage import data_to_media_item_artwork


def join_plural_field(field: list[str]) -> str | None:
	if field:
		return ", ".join(field)
	return None


def song_to_media_item(song: Song) -> NSMutableDictionary:
	nowplaying_info = NSMutableDictionary.dictionary()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeAudio
	nowplaying_info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = song.elapsed
	nowplaying_info[MPNowPlayingInfoPropertyExternalContentIdentifier] = str(song.file)
	nowplaying_info[MPMediaItemPropertyPersistentID] = song_to_persistent_id(song)

	nowplaying_info[MPMediaItemPropertyTitle] = song.title
	nowplaying_info[MPMediaItemPropertyArtist] = join_plural_field(song.artist)
	nowplaying_info[MPMediaItemPropertyAlbumTitle] = join_plural_field(song.album)
	nowplaying_info[MPMediaItemPropertyAlbumTrackNumber] = song.track
	nowplaying_info[MPMediaItemPropertyDiscNumber] = song.disc
	nowplaying_info[MPMediaItemPropertyGenre] = join_plural_field(song.genre)
	nowplaying_info[MPMediaItemPropertyComposer] = join_plural_field(song.composer)
	nowplaying_info[MPMediaItemPropertyPlaybackDuration] = song.duration

	if song.url is not None:
		nowplaying_info[MPNowPlayingInfoPropertyAssetURL] = song.url.human_repr()

	# MPD can't play back music at different rates, so we just want to set it
	# to 1.0 if the song is playing. (Set it to 0.0 if the song is paused.)
	rate = 1.0 if song.state == PlaybackState.play else 0.0
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackRate] = rate

	if song.art:
		artwork = data_to_media_item_artwork(song.art.data)
		nowplaying_info[MPMediaItemPropertyArtwork] = artwork

	return nowplaying_info
