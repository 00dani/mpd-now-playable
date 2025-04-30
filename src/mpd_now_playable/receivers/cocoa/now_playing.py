from collections.abc import Callable, Coroutine
from typing import Literal

from AppKit import NSApplication, NSApplicationActivationPolicyAccessory
from MediaPlayer import (
	MPChangePlaybackPositionCommandEvent,
	MPMusicPlaybackStatePlaying,
	MPNowPlayingInfoCenter,
	MPRemoteCommandCenter,
	MPRemoteCommandEvent,
	MPRemoteCommandHandlerStatus,
	MPRemoteCommandHandlerStatusSuccess,
)

from corefoundationasyncio import CoreFoundationEventLoop

from ...config.model import CocoaReceiverConfig
from ...playback import Playback
from ...playback.state import PlaybackState
from ...player import Player
from ...song_receiver import LoopFactory, Receiver
from ...tools.asyncio import run_background_task
from .convert.playback_to_media_item import playback_to_media_item
from .convert.to_state import playback_state_to_cocoa


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
		NSApplication.sharedApplication().setActivationPolicy_(
			NSApplicationActivationPolicyAccessory
		)
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

	async def update(self, playback: Playback) -> None:
		self.info_center.setNowPlayingInfo_(playback_to_media_item(playback))
		self.info_center.setPlaybackState_(playback_state_to_cocoa(playback.song.state))

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
