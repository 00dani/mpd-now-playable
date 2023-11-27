from collections.abc import Callable, Coroutine
from pathlib import Path

from AppKit import NSCompositingOperationCopy, NSImage, NSMakeRect
from Foundation import CGSize, NSMutableDictionary
from MediaPlayer import (
	MPMediaItemArtwork,
	MPMediaItemPropertyAlbumTitle,
	MPMediaItemPropertyArtist,
	MPMediaItemPropertyArtwork,
	MPMediaItemPropertyPlaybackDuration,
	MPMediaItemPropertyTitle,
	MPMusicPlaybackState,
	MPMusicPlaybackStatePaused,
	MPMusicPlaybackStatePlaying,
	MPMusicPlaybackStateStopped,
	MPNowPlayingInfoCenter,
	MPNowPlayingInfoMediaTypeAudio,
	MPNowPlayingInfoMediaTypeNone,
	MPNowPlayingInfoPropertyElapsedPlaybackTime,
	MPNowPlayingInfoPropertyMediaType,
	MPRemoteCommandCenter,
	MPRemoteCommandEvent,
	MPRemoteCommandHandlerStatus,
)

from .async_tools import run_background_task
from .player import Player
from .song import PlaybackState, Song


def logo_to_ns_image() -> NSImage:
	return NSImage.alloc().initByReferencingFile_(
		str(Path(__file__).parent / "mpd/logo.svg")
	)


def data_to_ns_image(data: bytes) -> NSImage:
	return NSImage.alloc().initWithData_(data)


def ns_image_to_media_item_artwork(img: NSImage) -> MPMediaItemArtwork:
	def resize(size: CGSize) -> NSImage:
		new = NSImage.alloc().initWithSize_(size)
		new.lockFocus()
		img.drawInRect_fromRect_operation_fraction_(
			NSMakeRect(0, 0, size.width, size.height),
			NSMakeRect(0, 0, img.size().width, img.size().height),
			NSCompositingOperationCopy,
			1.0,
		)
		new.unlockFocus()
		return new

	return MPMediaItemArtwork.alloc().initWithBoundsSize_requestHandler_(
		img.size(), resize
	)


def playback_state_to_cocoa(state: PlaybackState) -> MPMusicPlaybackState:
	return {
		PlaybackState.play: MPMusicPlaybackStatePlaying,
		PlaybackState.pause: MPMusicPlaybackStatePaused,
		PlaybackState.stop: MPMusicPlaybackStateStopped,
	}[state]


def song_to_media_item(song: Song) -> NSMutableDictionary:
	nowplaying_info = nothing_to_media_item()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeAudio
	nowplaying_info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = song.elapsed

	nowplaying_info[MPMediaItemPropertyTitle] = song.title
	nowplaying_info[MPMediaItemPropertyArtist] = song.artist
	nowplaying_info[MPMediaItemPropertyAlbumTitle] = song.album
	nowplaying_info[MPMediaItemPropertyPlaybackDuration] = song.duration

	if song.art:
		nowplaying_info[MPMediaItemPropertyArtwork] = ns_image_to_media_item_artwork(
			data_to_ns_image(song.art)
		)
	return nowplaying_info


def nothing_to_media_item() -> NSMutableDictionary:
	nowplaying_info = NSMutableDictionary.dictionary()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeNone
	nowplaying_info[MPMediaItemPropertyArtwork] = MPD_LOGO
	nowplaying_info[MPMediaItemPropertyTitle] = "MPD (stopped)"

	return nowplaying_info


MPD_LOGO = ns_image_to_media_item_artwork(logo_to_ns_image())


class CocoaNowPlaying:
	def __init__(self, player: Player):
		self.cmd_center = MPRemoteCommandCenter.sharedCommandCenter()
		self.info_center = MPNowPlayingInfoCenter.defaultCenter()

		cmds = (
			(self.cmd_center.togglePlayPauseCommand(), player.on_play_pause),
			(self.cmd_center.playCommand(), player.on_play),
			(self.cmd_center.pauseCommand(), player.on_pause),
			(self.cmd_center.stopCommand(), player.on_stop),
			(self.cmd_center.nextTrackCommand(), player.on_next),
			(self.cmd_center.previousTrackCommand(), player.on_prev),
		)

		for cmd, handler in cmds:
			cmd.setEnabled_(True)
			cmd.removeTarget_(None)
			cmd.addTargetWithHandler_(self._create_handler(handler))

		unsupported_cmds = (
			self.cmd_center.changePlaybackRateCommand(),
			self.cmd_center.seekBackwardCommand(),
			self.cmd_center.skipBackwardCommand(),
			self.cmd_center.seekForwardCommand(),
			self.cmd_center.skipForwardCommand(),
			self.cmd_center.changePlaybackPositionCommand(),
		)
		for cmd in unsupported_cmds:
			cmd.setEnabled_(False)

		# If MPD is paused when this bridge starts up, we actually want the now
		# playing info center to see a playing -> paused transition, so we can
		# unpause with remote commands.
		self.info_center.setPlaybackState_(MPMusicPlaybackStatePlaying)

	def update(self, song: Song | None) -> None:
		if song:
			self.info_center.setNowPlayingInfo_(song_to_media_item(song))
			self.info_center.setPlaybackState_(playback_state_to_cocoa(song.state))
		else:
			self.info_center.setNowPlayingInfo_(nothing_to_media_item())
			self.info_center.setPlaybackState_(MPMusicPlaybackStateStopped)

	def _create_handler(
		self, player: Callable[[], Coroutine[None, None, PlaybackState | None]]
	) -> Callable[[MPRemoteCommandEvent], None]:
		async def invoke_music_player() -> None:
			result = await player()
			if result:
				self.info_center.setPlaybackState_(playback_state_to_cocoa(result))

		def handler(event: MPRemoteCommandEvent) -> MPRemoteCommandHandlerStatus:
			run_background_task(invoke_music_player())
			return 0

		return handler
