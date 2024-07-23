from collections.abc import Callable
from typing import Final, Literal, override

from AppKit import NSImage
from Foundation import CGSize, NSMutableDictionary

MPMusicPlaybackStateStopped: Final = 0
MPMusicPlaybackStatePlaying: Final = 1
MPMusicPlaybackStatePaused: Final = 2
MPMusicPlaybackState = Literal[0, 1, 2]

MPMediaItemPropertyAlbumTitle: Final = "albumTitle"
MPMediaItemPropertyAlbumTrackNumber: Final = "albumTrackNumber"
MPMediaItemPropertyDiscNumber: Final = "discNumber"
MPMediaItemPropertyGenre: Final = "genre"
MPMediaItemPropertyArtist: Final = "artist"
MPMediaItemPropertyComposer: Final = "composer"
MPMediaItemPropertyArtwork: Final = "artwork"
MPMediaItemPropertyPlaybackDuration: Final = "playbackDuration"
MPMediaItemPropertyPersistentID: Final = "persistentID"
MPMediaItemPropertyTitle: Final = "title"

MPNowPlayingInfoPropertyMediaType: Final = "MPNowPlayingInfoPropertyMediaType"
MPNowPlayingInfoMediaTypeAudio: Final = 1
MPNowPlayingInfoMediaTypeNone: Final = 0

MPNowPlayingInfoPropertyPlaybackRate: Final = "MPNowPlayingInfoPropertyPlaybackRate"
MPNowPlayingInfoPropertyPlaybackQueueCount: Final = (
	"MPNowPlayingInfoPropertyPlaybackQueueCount"
)
MPNowPlayingInfoPropertyPlaybackQueueIndex: Final = (
	"MPNowPlayingInfoPropertyPlaybackQueueIndex"
)
MPNowPlayingInfoPropertyElapsedPlaybackTime: Final = (
	"MPNowPlayingInfoPropertyElapsedPlaybackTime"
)
MPNowPlayingInfoPropertyAssetURL: Final = "MPNowPlayingInfoPropertyAssetURL"
MPNowPlayingInfoPropertyExternalContentIdentifier: Final = (
	"MPNowPlayingInfoPropertyExternalContentIdentifier"
)

class MPMediaItemArtwork:
	@staticmethod
	def alloc() -> type[MPMediaItemArtwork]: ...
	@staticmethod
	def initWithBoundsSize_requestHandler_(
		size: CGSize, handler: Callable[[CGSize], NSImage]
	) -> MPMediaItemArtwork: ...

class MPNowPlayingInfoCenter:
	@staticmethod
	def defaultCenter() -> MPNowPlayingInfoCenter: ...
	def setNowPlayingInfo_(self, info: NSMutableDictionary) -> None: ...
	def setPlaybackState_(self, state: MPMusicPlaybackState) -> None: ...

MPRemoteCommandHandlerStatusSuccess: Final = 0
MPRemoteCommandHandlerStatusCommandFailed: Final = 200
MPRemoteCommandHandlerStatus = Literal[0, 200]

class MPRemoteCommandEvent:
	pass

class MPChangePlaybackPositionCommandEvent(MPRemoteCommandEvent):
	def positionTime(self) -> float:
		"""Return the requested playback position as a number of seconds (fractional seconds are allowed)."""
		pass

class MPRemoteCommand:
	def setEnabled_(self, enabled: bool) -> None: ...
	def removeTarget_(self, target: object) -> None: ...
	def addTargetWithHandler_(
		self, handler: Callable[[MPRemoteCommandEvent], MPRemoteCommandHandlerStatus]
	) -> None:
		"""Register a callback to handle the commands. Many remote commands don't carry useful information in the event object (play, pause, next track, etc.), so the callback does not necessarily need to care about the event argument."""
		pass

class MPChangePlaybackPositionCommand(MPRemoteCommand):
	@override
	def addTargetWithHandler_(
		self,
		handler: Callable[
			[MPChangePlaybackPositionCommandEvent], MPRemoteCommandHandlerStatus
		],
	) -> None: ...

class MPRemoteCommandCenter:
	@staticmethod
	def sharedCommandCenter() -> MPRemoteCommandCenter: ...
	def togglePlayPauseCommand(self) -> MPRemoteCommand: ...
	def playCommand(self) -> MPRemoteCommand: ...
	def pauseCommand(self) -> MPRemoteCommand: ...
	def stopCommand(self) -> MPRemoteCommand: ...
	def nextTrackCommand(self) -> MPRemoteCommand: ...
	def previousTrackCommand(self) -> MPRemoteCommand: ...
	def changePlaybackRateCommand(self) -> MPRemoteCommand: ...
	def seekBackwardCommand(self) -> MPRemoteCommand: ...
	def skipBackwardCommand(self) -> MPRemoteCommand: ...
	def seekForwardCommand(self) -> MPRemoteCommand: ...
	def skipForwardCommand(self) -> MPRemoteCommand: ...
	def changePlaybackPositionCommand(self) -> MPChangePlaybackPositionCommand: ...
