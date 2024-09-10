import os
from pathlib import Path
from manim_recorder.helper import msg_box, get_audio_basename
from manim_recorder.recorder.base import AudioService
from manim import logger

from manim_recorder.recorder.server.app import WebRecorder


class RecorderService(AudioService):
    """Speech service that records from a microphone during rendering."""

    def __init__(
        self,
        **kwargs,
    ):
        """Initialize the speech service.

        Args:
            format (int, optional): Format of the audio. Defaults to pyaudio.paInt16.
            channels (int, optional): Number of channels. Defaults to 1.
            rate (int, optional): Sampling rate. Defaults to 44100.
            chunk (int, optional): Chunk size. Defaults to 512.
            device_index (int, optional): Device index, if you don't want to choose it every time you render. Defaults to None.
            trim_silence_threshold (float, optional): Threshold for trimming silence in decibels. Defaults to -40.0 dB.
            trim_buffer_start (int, optional): Buffer duration for trimming silence at the start. Defaults to 200 ms.
            trim_buffer_end (int, optional): Buffer duration for trimming silence at the end. Defaults to 200 ms.
        """
        self.app = WebRecorder(package_dir=os.getcwd())

        AudioService.__init__(self, **kwargs)

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None, **kwargs
    ) -> dict:
        """"""

        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            # Remove bookmarks so that we don't record a voiceover every time we change a bookmark
            "input_text": text,
            "config": {
                'status': 'success'
            }
        }
        cached_result = self.get_cached_result(input_data, cache_dir, **kwargs)

        if cached_result is not None:
            return cached_result

        audio_path = get_audio_basename() + ".wav" if path is None else path
        self.app.record(str(Path(cache_dir) / audio_path), text)
        self.app.run()
        
        # self.recorder.record(str(Path(cache_dir) / audio_path), text)

        json_dict = {
            "input_data": input_data,
            "original_audio": audio_path
        }

        return json_dict
