from hashlib import blake2b
from pathlib import Path
from typing import Final
from uuid import UUID

from ...song import Song

# The maximum size for a BLAKE2b "person" value is sixteen bytes, so we need to be concise.
HASH_PERSON_PREFIX: Final = b"mnp.mac."
RECORDING_ID_HASH_PERSON: Final = HASH_PERSON_PREFIX + b"mb_rid"
TRACK_ID_HASH_PERSON: Final = HASH_PERSON_PREFIX + b"mb_tid"
FILE_HASH_PERSON: Final = HASH_PERSON_PREFIX + b"f"

PERSISTENT_ID_BITS: Final = 64
PERSISTENT_ID_BYTES: Final = PERSISTENT_ID_BITS // 8


def digest_recording_id(recording_id: UUID) -> bytes:
	return blake2b(
		recording_id.bytes,
		digest_size=PERSISTENT_ID_BYTES,
		person=RECORDING_ID_HASH_PERSON,
	).digest()


def digest_track_id(track_id: UUID) -> bytes:
	return blake2b(
		track_id.bytes,
		digest_size=PERSISTENT_ID_BYTES,
		person=TRACK_ID_HASH_PERSON,
	).digest()


def digest_file_uri(file: Path) -> bytes:
	return blake2b(
		bytes(file), digest_size=PERSISTENT_ID_BYTES, person=FILE_HASH_PERSON
	).digest()


# The MPMediaItemPropertyPersistentID is only 64 bits, while a UUID is 128
# bits and not all tracks will even have their MusicBrainz track ID included.
# To work around this, we compute a BLAKE2 hash from the UUID, or failing
# that from the file URI. BLAKE2 can be customised to different digest sizes,
# making it perfect for this problem.
def song_to_persistent_id(song: Song) -> int:
	if song.musicbrainz.recording:
		hashed_id = digest_recording_id(song.musicbrainz.recording)
	elif song.musicbrainz.track:
		hashed_id = digest_track_id(song.musicbrainz.track)
	else:
		hashed_id = digest_file_uri(song.file)
	return int.from_bytes(hashed_id)
