from __future__ import annotations

from simple_audio_player import SimpleAudioPlayer
from song_service import SongService

INITIAL_SONG_ID = -1

# TODO: Needs to accept a SongService, or a member of a interface that SongService can implement.
#        Very hard to test as-is.

class ManagedAudioPlayer(SimpleAudioPlayer):
    """An audio player that supports getting the next/previous song from an underlying song service.
    Use the next_song/previous_song"""
    def __init__(self):
        super().__init__()
        self._current_song_id: int = INITIAL_SONG_ID
        self._song_service: SongService = SongService()

        self._song_service.start_service()

    def play_current_song(self) -> bool:
        """Will attempt to play the current song. Returns whether or not playing succeeded.
        Will fail if there are no available songs to play.
        Blocks until playback finishes."""
        if self._current_song_id == INITIAL_SONG_ID:
            if self._song_service.song_available():
                self.next_song()
            else:
                return False
        else:
            song_path = self._song_service.get_song_path_by_song_id(self._current_song_id)
            if song_path is None:  # Should never be None since we checked for songs above.
                return False
            else:
                # Blocking
                self.play_from_path(song_path)
                return True

    def next_song(self) -> bool:
        """Advances to the next song. Returns whether or not advancing succeeded.
        Will fail if there are no available songs to play in the song service.
        Does not affect playback of the current song. Call play_current_song after to play the song."""
        available_songs = len(self._song_service)
        next_song_id = self._current_song_id + 1

        if next_song_id < available_songs:
            self._current_song_id = next_song_id
            return True
        else:
            return False

    def previous_song(self) -> bool:
        """Goes back to the previous song. Returns whether or not retreating succeeded.
        Will fail if there are no available songs to go back to.
        Does not affect playback of the current song. Call play_current_song after to play the song."""
        if self._current_song_id < 1:
            return False
        else:
            self._current_song_id -= 1
            return True

    def terminate(self) -> None:
        super().terminate()
        self._song_service.terminate_service()

    def __enter__(self) -> ManagedAudioPlayer:
        return self

    def __exit__(self, *_) -> None:
        self.terminate()