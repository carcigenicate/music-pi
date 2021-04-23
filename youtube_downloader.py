from os import PathLike
from typing import Union

import youtube_dl
from pathlib import PurePath

AUDIO_DOWNLOAD_OPTIONS = \
    {'format': "worstaudio/worst",
     'postprocessors': [{
         'key': 'FFmpegExtractAudio',
         'preferredcodec': 'mp3',
         'preferredquality': '192'}],
     #'outtmpl': "./%(id)s.%(ext)s",  # https://github.com/ytdl-org/youtube-dl/blob/master/README.md#output-template
     'quiet': "true"  # False for debugging, True for "production"
     }


BASE_URL = "https://www.youtube.com/watch?v="


def download_audio(video_id: str, download_directory: Union[str, bytes, PathLike]) -> None:
    """Downloads the audio to the provided location.
    The filename matches the video ID."""
    # Making a copy so the global settings aren't mutated.
    options = dict(AUDIO_DOWNLOAD_OPTIONS)
    save_path = str(PurePath(download_directory) / "%(id)s.%(ext)s")
    options['outtmpl'] = save_path
    with youtube_dl.YoutubeDL(options) as dl:
        dl.download([BASE_URL + video_id])