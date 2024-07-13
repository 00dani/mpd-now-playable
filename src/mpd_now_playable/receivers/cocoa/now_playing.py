from collections.abc import Callable, Coroutine
from pathlib import Path
from typing import Literal

from AppKit import NSCompositingOperationCopy, NSImage, NSMakeRect
from corefoundationasyncio import CoreFoundationEventLoop
from Foundation import CGSize, NSMutableDictionary
from MediaPlayer import (
	MPChangePlaybackPositionCommandEvent,
	MPMediaItemArtwork,
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
	MPMusicPlaybackState,
	MPMusicPlaybackStatePaused,
	MPMusicPlaybackStatePlaying,
	MPMusicPlaybackStateStopped,
	MPNowPlayingInfoCenter,
	MPNowPlayingInfoMediaTypeAudio,
	MPNowPlayingInfoMediaTypeNone,
	MPNowPlayingInfoPropertyElapsedPlaybackTime,
	MPNowPlayingInfoPropertyExternalContentIdentifier,
	MPNowPlayingInfoPropertyMediaType,
	MPNowPlayingInfoPropertyPlaybackQueueCount,
	MPNowPlayingInfoPropertyPlaybackQueueIndex,
	MPNowPlayingInfoPropertyPlaybackRate,
	MPRemoteCommandCenter,
	MPRemoteCommandEvent,
	MPRemoteCommandHandlerStatus,
	MPRemoteCommandHandlerStatusSuccess,
)

from ...config.model import CocoaReceiverConfig
from ...player import Player
from ...song import PlaybackState, Song
from ...song_receiver import LoopFactory, Receiver
from ...tools.asyncio import run_background_task
from .persistent_id import song_to_persistent_id


def logo_to_ns_image() -> NSImage:
	return NSImage.alloc().initByReferencingFile_(
		str(Path(__file__).parent.parent.parent / "mpd/logo.svg")
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
	mapping: dict[PlaybackState, MPMusicPlaybackState] = {
		PlaybackState.play: MPMusicPlaybackStatePlaying,
		PlaybackState.pause: MPMusicPlaybackStatePaused,
		PlaybackState.stop: MPMusicPlaybackStateStopped,
	}
	return mapping[state]


def join_plural_field(field: list[str]) -> str | None:
	if field:
		return ", ".join(field)
	return None


def song_to_media_item(song: Song) -> NSMutableDictionary:
	nowplaying_info = nothing_to_media_item()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeAudio
	nowplaying_info[MPNowPlayingInfoPropertyElapsedPlaybackTime] = song.elapsed
	nowplaying_info[MPNowPlayingInfoPropertyExternalContentIdentifier] = str(song.file)
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackQueueCount] = song.queue_length
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackQueueIndex] = song.queue_index
	nowplaying_info[MPMediaItemPropertyPersistentID] = song_to_persistent_id(song)

	nowplaying_info[MPMediaItemPropertyTitle] = song.title
	nowplaying_info[MPMediaItemPropertyArtist] = join_plural_field(song.artist)
	nowplaying_info[MPMediaItemPropertyAlbumTitle] = join_plural_field(song.album)
	nowplaying_info[MPMediaItemPropertyAlbumTrackNumber] = song.track
	nowplaying_info[MPMediaItemPropertyDiscNumber] = song.disc
	nowplaying_info[MPMediaItemPropertyGenre] = join_plural_field(song.genre)
	nowplaying_info[MPMediaItemPropertyComposer] = join_plural_field(song.composer)
	nowplaying_info[MPMediaItemPropertyPlaybackDuration] = song.duration

	# MPD can't play back music at different rates, so we just want to set it
	# to 1.0 if the song is playing. (Leave it at 0.0 if the song is paused.)
	if song.state == PlaybackState.play:
		nowplaying_info[MPNowPlayingInfoPropertyPlaybackRate] = 1.0

	if song.art:
		nowplaying_info[MPMediaItemPropertyArtwork] = ns_image_to_media_item_artwork(
			data_to_ns_image(song.art.data)
		)
	return nowplaying_info


def nothing_to_media_item() -> NSMutableDictionary:
	nowplaying_info = NSMutableDictionary.dictionary()
	nowplaying_info[MPNowPlayingInfoPropertyMediaType] = MPNowPlayingInfoMediaTypeNone
	nowplaying_info[MPMediaItemPropertyArtwork] = MPD_LOGO
	nowplaying_info[MPMediaItemPropertyTitle] = "MPD (stopped)"
	nowplaying_info[MPNowPlayingInfoPropertyPlaybackRate] = 0.0

	return nowplaying_info


MPD_LOGO = ns_image_to_media_item_artwork(logo_to_ns_image())


class CocoaLoopFactory(LoopFactory[CoreFoundationEventLoop]):
	@property
	def is_replaceable(self) -> Literal[False]:
		return False

	@classmethod
	def make_loop(cls) -> CoreFoundationEventLoop:
		return CoreFoundationEventLoop(console_app=True)


class CocoaNowPlayingReceiver(Receiver):
	@classmethod
	def loop_factory(cls) -> LoopFactory[CoreFoundationEventLoop]:
		return CocoaLoopFactory()

	def __init__(self, config: CocoaReceiverConfig):
		pass

	async def start(self, player: Player) -> None:
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

		seekCmd = self.cmd_center.changePlaybackPositionCommand()
		seekCmd.setEnabled_(True)
		seekCmd.removeTarget_(None)
		seekCmd.addTargetWithHandler_(self._create_seek_handler(player.on_seek))

		unsupported_cmds = (
			self.cmd_center.changePlaybackRateCommand(),
			self.cmd_center.seekBackwardCommand(),
			self.cmd_center.skipBackwardCommand(),
			self.cmd_center.seekForwardCommand(),
			self.cmd_center.skipForwardCommand(),
		)
		for cmd in unsupported_cmds:
			cmd.setEnabled_(False)

		# If MPD is paused when this bridge starts up, we actually want the now
		# playing info center to see a playing -> paused transition, so we can
		# unpause with remote commands.
		self.info_center.setPlaybackState_(MPMusicPlaybackStatePlaying)

	async def update(self, song: Song | None) -> None:
		if song:
			self.info_center.setNowPlayingInfo_(song_to_media_item(song))
			self.info_center.setPlaybackState_(playback_state_to_cocoa(song.state))
		else:
			self.info_center.setNowPlayingInfo_(nothing_to_media_item())
			self.info_center.setPlaybackState_(MPMusicPlaybackStateStopped)

	def _create_handler(
		self, player: Callable[[], Coroutine[None, None, PlaybackState | None]]
	) -> Callable[[MPRemoteCommandEvent], MPRemoteCommandHandlerStatus]:
		async def invoke_music_player() -> None:
			result = await player()
			if result:
				self.info_center.setPlaybackState_(playback_state_to_cocoa(result))

		def handler(event: MPRemoteCommandEvent) -> MPRemoteCommandHandlerStatus:
			run_background_task(invoke_music_player())
			return 0

		return handler

	def _create_seek_handler(
		self, player: Callable[[float], Coroutine[None, None, None]]
	) -> Callable[[MPChangePlaybackPositionCommandEvent], MPRemoteCommandHandlerStatus]:
		def handler(
			event: MPChangePlaybackPositionCommandEvent,
		) -> MPRemoteCommandHandlerStatus:
			run_background_task(player(event.positionTime()))
			return MPRemoteCommandHandlerStatusSuccess

		return handler
