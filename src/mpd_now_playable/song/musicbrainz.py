from dataclasses import dataclass
from functools import partial
from typing import Annotated, TypedDict
from uuid import UUID

from pydantic import Field

from ..tools.types import option_fmap

option_uuid = partial(option_fmap, UUID)
OptionUUID = Annotated[UUID | None, Field(default=None)]


class MusicBrainzTags(TypedDict, total=False):
	"""
	The MusicBrainz tags mpd-now-playable expects and will load (all optional).
	They're named slightly differently than the actual MusicBrainz IDs they
	store - use to_brainz to map them across to their canonical form.
	https://picard-docs.musicbrainz.org/downloads/MusicBrainz_Picard_Tag_Map.html
	"""

	#: MusicBrainz Recording ID
	musicbrainz_trackid: str
	#: MusicBrainz Track ID
	musicbrainz_releasetrackid: str
	#: MusicBrainz Artist ID
	musicbrainz_artistid: str
	#: MusicBrainz Release ID
	musicbrainz_albumid: str
	#: MusicBrainz Release Artist ID
	musicbrainz_albumartistid: str
	#: MusicBrainz Release Group ID
	musicbrainz_releasegroupid: str
	#: MusicBrainz Work ID
	musicbrainz_workid: str


@dataclass(slots=True)
class MusicBrainzIds:
	#: A MusicBrainz recording represents audio from a specific performance.
	#: For example, if the same song was released as a studio recording and as
	#: a live performance, those two versions of the song are different
	#: recordings. The song itself is considered a "work", of which two
	#: recordings were made. However, recordings are not always associated with
	#: a work in the MusicBrainz database, and Picard won't load work IDs by
	#: default (you have to enable "use track relationships" in the options),
	#: so recording IDs are a much more reliable way to identify a particular
	#: song.
	#: https://musicbrainz.org/doc/Recording
	recording: OptionUUID

	#: A MusicBrainz work represents the idea of a particular song or creation
	#: (it doesn't have to be audio). Each work may have multiple recordings
	#: (studio versus live, different performers, etc.), with the work ID
	#: grouping them together.
	#: https://musicbrainz.org/doc/Work
	work: OptionUUID

	#: A MusicBrainz track represents a specific instance of a recording
	#: appearing as part of some release. For example, if the same song appears
	#: on both two-CD and four-CD versions of a soundtrack, then it will be
	#: considered the same "recording" in both cases, but different "tracks".
	#: https://musicbrainz.org/doc/Track
	track: OptionUUID

	#: https://musicbrainz.org/doc/Artist
	artist: OptionUUID

	#: A MusicBrainz release roughly corresponds to an "album", and indeed is
	#: stored in a tag called MUSICBRAINZ_ALBUMID. The more general name is
	#: meant to encompass all the different ways music can be released.
	#: https://musicbrainz.org/doc/Release
	release: OptionUUID

	#: Again, the release artist corresponds to an "album artist". These MBIDs
	#: refer to the same artists in the MusicBrainz database that individual
	#: recordings' artist MBIDs do.
	release_artist: OptionUUID

	#: A MusicBrainz release group roughly corresponds to "all the editions of
	#: a particular album". For example, if the same album were released on CD,
	#: vinyl records, and as a digital download, then all of those would be
	#: different releases but share a release group. Note that MPD's support
	#: for this tag is relatively new (July 2023) and doesn't seem especially
	#: reliable, so it might be missing here even if your music has been tagged
	#: with it. Not sure why. https://musicbrainz.org/doc/Release_Group
	release_group: OptionUUID


def to_brainz(tags: MusicBrainzTags) -> MusicBrainzIds:
	return MusicBrainzIds(
		recording=option_uuid(tags.get("musicbrainz_trackid")),
		work=option_uuid(tags.get("musicbrainz_workid")),
		track=option_uuid(tags.get("musicbrainz_releasetrackid")),
		artist=option_uuid(tags.get("musicbrainz_artistid")),
		release=option_uuid(tags.get("musicbrainz_albumid")),
		release_artist=option_uuid(tags.get("musicbrainz_albumartistid")),
		release_group=option_uuid(tags.get("musicbrainz_releasegroupid")),
	)
