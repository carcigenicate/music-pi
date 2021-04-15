from __future__ import annotations
import subprocess as sp
from logging_util import setup_logger

player_logger = setup_logger("player", "player.log")

COMMAND = "mpg123 -R"

# Commands are only characters in the ASCII set.
STDIN_ENCODING = "ascii"

END_PLAYBACK_SENTINEL = b"@P 0"
ERROR_SENTINEL = b"@E"


def clamp(n: int, min_n: int, max_n: int) -> int:
    return min(max_n, max(min_n, n))


class SimpleAudioPlayer:
    """An audio player wrapper over mpg123 that allows for control of playback."""
    def __init__(self):
        self._player_process: sp.Popen = sp.Popen(COMMAND.split(), stdin=sp.PIPE, stdout=sp.PIPE, stderr=sp.DEVNULL)

        # mpg123 does absolute volume setting. To avoid needing to do a lookup to set volume, we're maintaining
        #  and internal volume level. This value is relative to and independent of the system volume.
        self._volume = 100
        # To ensure that the real and "cached" volumes are in sync.
        self.set_volume(self._volume)

    def _send_command(self, command: str) -> None:
        # Apparently, writing directly to the STDIN can cause dead-locks, according to the Python documentation.
        # The alternative though (.communicate) don't work when sending commands without wanting to wait for the
        #  process to terminate.
        self._player_process.stdin.write(command.encode(STDIN_ENCODING) + b"\n")
        self._player_process.stdin.flush()

    def play_from_path(self, song_path: str) -> None:
        """Starts playing the given song. Blocks until the song finishes."""
        self._send_command(f"load {song_path}")

        # mpg123 -R outputs a certain sentinel line when playback has finished, or when an error happens.
        while True:
            line = self._player_process.stdout.readline()
            if line.startswith(ERROR_SENTINEL):
                player_logger.error(line.removeprefix(ERROR_SENTINEL))
            if line.startswith(END_PLAYBACK_SENTINEL) or not line:
                break

    def stop(self) -> None:
        self._send_command("stop")

    def toggle_pause(self) -> None:
        self._send_command("pause")

    def set_volume(self, new_volume: int) -> None:
        self._volume = clamp(new_volume, 0, 100)
        self._send_command(f"volume {self._volume}")

    def adjust_volume(self, adjust_amount: int) -> None:
        """The provided adjustment should be an integer between -100 and 100 indicating how much to adjust the
        volume by. Negative numbers decrease volume, positive numbers increase."""
        self.set_volume(self._volume + adjust_amount)

    def seek_by(self, seek_by: int) -> None:
        self._send_command(f"seek {seek_by:+f}")

    def pitch_adj(self, adj: float) -> None:
        self._send_command(f"pitch {adj:+f}")

    def pitch_set(self, pitch: float) -> None:
        self._send_command(f"pitch {pitch:f}")

    def terminate(self):
        """Should be called either directly or via a context manager to terminate the player process."""
        self._player_process.terminate()

    def __enter__(self) -> SimpleAudioPlayer:
        return self

    def __exit__(self, *_) -> None:
        self.terminate()
