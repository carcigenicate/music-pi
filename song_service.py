from __future__ import annotations

import os
from multiprocessing import Process, Queue
from os.path import isfile
from pathlib import Path, PurePath
from random import choices
from string import ascii_letters
from typing import Optional, Tuple, Iterator

from paho.mqtt.subscribe import callback as subscribe_with_callback
from youtube_dl.utils import YoutubeDLError

from logging_util import setup_logger
from song_database import IDCache
from youtube_downloader import download_audio

PAYLOAD_ENCODING = "UTF-8"
MUSIC_EXTENSION = "mp3"

SUBSCRIBE_TOPIC = "request"
HOSTNAME = "192.168.50.156"
CLIENT_ID_BASE = "MusicPiClient"
CLIENT_ID_POST_LENGTH = 5

USERNAME = "reproject"
PASSWORD = "reproject"


# The current folder. Prevents relying on the CWD, which may cause problems if the client
#   is started from a different directory.
PROJECT_PATH = Path(__file__).parent.absolute()
DOWNLOAD_DIRECTORY = PROJECT_PATH / "download"

service_logger = setup_logger("song_service", "song_service.log")


def _song_path(youtube_id: str) -> str:
    return f"{PurePath(DOWNLOAD_DIRECTORY) / youtube_id}.{MUSIC_EXTENSION}"

def _clear_downloaded() -> None:
    """Deletes all regular files in the download directory."""
    for file in os.listdir(DOWNLOAD_DIRECTORY):
        path = PurePath(DOWNLOAD_DIRECTORY, file)
        if isfile(path):
            os.remove(path)


# Can have song_id (or get_next_song) requests given to it
class SongService:
    def __init__(self):
        self._available_song_ids: IDCache = IDCache()

        self._receive_queue: Queue = Queue()  # The queue of what requests have been received. Waiting to be downloaded.
        self._downloaded_queue: Queue = Queue()  # The queue of what has finished downloading. Waiting to be acknowledged.

        # So processing of receiving and downloading doesn't bog down the main process.
        # Since it's mostly IO, threads should work here as well, but multiprocessing will allow for more parallelism.
        self._receive_process = self._new_receiver_process()
        self._download_process = self._new_downloader_process()

    def _new_receiver_process(self) -> Process:
        """Creates and returns a new process that will put messages (video IDs) into the passed queue as they come in.
        The process is not started."""

        def callback(client, user_data, message):
            # Can block if the queue is full.
            self._receive_queue.put(message.payload.decode(PAYLOAD_ENCODING))

        def receive_incoming_messages():
            message_logger = setup_logger("messages", "messages.log")
            try:
                # If all instances have the same ID and this process gets stuck open somehow, it will cause problems as
                # soon as another client with the same client ID connects (reconnecting loop between two processes).
                randomized_client_id = f"{CLIENT_ID_BASE}_{''.join(choices(ascii_letters, k=CLIENT_ID_POST_LENGTH))}"
                auth = {"username": USERNAME, "password": PASSWORD}
                # Blocks forever.
                subscribe_with_callback(callback=callback,
                                        topics=[SUBSCRIBE_TOPIC],
                                        hostname=HOSTNAME,
                                        client_id=randomized_client_id,
                                        auth=auth,
                                        keepalive=60)
            except ConnectionRefusedError as e:
                message_logger.warning("Could not contact the MQTT server.")
                # Just to give a slightly cleaner message to the user.
                raise ConnectionRefusedError("Could not reach MQTT server.") from e
            except Exception as e:
                message_logger.warning(f"Unknown exception: {e}")
                raise type(e)(f"Unknown Exception: {e}") from e
            except KeyboardInterrupt:
                pass

        return Process(target=receive_incoming_messages, daemon=True)

    def _new_downloader_process(self) -> Process:
        def process_video_requests():
            dl_logger = setup_logger("download", "download.log")
            youtube_id = None  # To make the static analyzer happy in the except block.
            try:
                while True:
                    youtube_id = self._receive_queue.get()
                    download_audio(youtube_id, DOWNLOAD_DIRECTORY)  # A long, blocking call
                    self._downloaded_queue.put(youtube_id)
            except YoutubeDLError as e:
                dl_logger.warning(f"Error downloading video ID {youtube_id}: {e}")
            except Exception as e:
                dl_logger.warning(f"Unknown exception: {e}")
                raise type(e)(f"Unknown Exception: {e}") from e
            except KeyboardInterrupt:
                pass

        return Process(target=process_video_requests, daemon=True)

    def _process_downloaded_queue(self):
        """An unfortunate consequence of multiprocessing. It would be difficult to handle this in child process due to
        IPC making copies of objects when sending them between processes.
        Should be called before any operation that uses the ID cache."""
        try:
            while not self._downloaded_queue.empty():
                downloaded_youtube_id = self._downloaded_queue.get()
                self._available_song_ids.register_song(downloaded_youtube_id)
        except OSError as e:
            # TODO: .empty() can cause an "handle is closed" error during termination.
            service_logger.warning(e)

    def get_song_path_by_song_id(self, song_id: int) -> Optional[str]:
        """Gets the youtube ID at the given song ID, if that song ID is available.
        If no such song ID exists, None is returned."""
        self._process_downloaded_queue()
        youtube_id = self._available_song_ids.get_youtube_id_from_song_id(song_id)

        if youtube_id is None:
            return None
        else:
            return _song_path(youtube_id)

    def __iter__(self) -> Iterator[Tuple[int, str]]:
        """Returns an iterator of all downloaded songs as tuples of (song_id, youtube_id)."""
        self._process_downloaded_queue()
        return iter(self._available_song_ids)

    def __len__(self) -> int:
        """Returns how many songs are available."""
        self._process_downloaded_queue()
        return len(self._available_song_ids)

    def song_available(self) -> bool:
        return len(self) > 0

    @staticmethod
    def _clear_downloaded() -> None:
        """Deletes all regular files in the download directory."""
        for file in os.listdir(DOWNLOAD_DIRECTORY):
            path = PurePath(DOWNLOAD_DIRECTORY, file)
            if isfile(path):
                os.remove(path)

    def start_service(self) -> None:
        """Starts the service. Must be called before any other methods."""
        self._receive_process.start()
        self._download_process.start()

    def terminate_service(self) -> None:
        """Closes all resources associated with the service. Must be called for a clean shutdown."""
        self._receive_process.terminate()
        self._download_process.terminate()
        self._receive_process.join()
        self._download_process.join()
        self._receive_process.close()
        self._download_process.close()

        self._receive_queue.close()
        self._downloaded_queue.close()

        _clear_downloaded()

    def __enter__(self) -> SongService:
        self.start_service()
        return self

    def __exit__(self, *_) -> None:
        self.terminate_service()
