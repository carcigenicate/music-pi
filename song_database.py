from typing import Dict, Optional, Iterator, Tuple

# yid = "YouTube ID". The video ID in the URL.
# sid = The local song ID, unrelated to the YouTube ID. Used for sequencing.

class IDCache:
    """Maintains bidirectional associations between YouTube video IDs and song sequence IDs."""
    def __init__(self):
        self._next_id = 0

        # Emulating a bidirectional dictionary
        self._sid_to_yid: Dict[int, str] = {}
        self._yid_to_sid: Dict[str, int] = {}

    def _associate(self, song_id: int, youtube_id: str) -> None:
        self._sid_to_yid[song_id] = youtube_id
        self._yid_to_sid[youtube_id] = song_id

    def register_song(self, youtube_id: str) -> int:
        """Registers a song into the database. Returns the ID of the inserted song."""
        existing_id = self._yid_to_sid.get(youtube_id)
        if existing_id is None:
            song_id = self._next_id
            self._next_id += 1
            self._associate(song_id, youtube_id)
            return song_id
        else:
            return existing_id

    def get_youtube_id_from_song_id(self, song_id: int) -> Optional[str]:
        return self._sid_to_yid.get(song_id)

    def get_song_id_from_youtube_id(self, youtube_id: str) -> Optional[int]:
        return self._yid_to_sid.get(youtube_id)

    def next_song_id(self) -> int:
        return self._next_id

    def __iter__(self) -> Iterator[Tuple[int, str]]:
        """Produces tuples of (song_id, youtube_id)."""
        return iter((k, v) for k, v in self._sid_to_yid.items())

    def __len__(self) -> int:
        return len(self._sid_to_yid)
