from collections.abc import Callable
from typing import Final, Literal

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

MPNowPlayingInfoPropertyPlaybackQueueCount: Final = (
	"MPNowPlayingInfoPropertyPlaybackQueueCount"
)
MPNowPlayingInfoPropertyPlaybackQueueIndex: Final = (
	"MPNowPlayingInfoPropertyPlaybackQueueIndex"
)
MPNowPlayingInfoPropertyElapsedPlaybackTime: Final = (
	"MPNowPlayingInfoPropertyElapsedPlaybackTime"
)
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

MPRemoteCommandHandlerStatusSuccess: Literal[0] = 0
MPRemoteCommandHandlerStatusCommandFailed: Literal[200] = 200
MPRemoteCommandHandlerStatus = Literal[0, 200]

class MPRemoteCommandEvent:
	pass

class MPRemoteCommand:
	def setEnabled_(self, enabled: bool) -> None: ...
	def removeTarget_(self, target: object) -> None: ...
	def addTargetWithHandler_(
		self, handler: Callable[[MPRemoteCommandEvent], MPRemoteCommandHandlerStatus]
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
	def changePlaybackPositionCommand(self) -> MPRemoteCommand: ...
