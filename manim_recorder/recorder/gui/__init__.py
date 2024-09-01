from pathlib import Path
from manim_recorder.helper import msg_box
from manim_recorder.recorder.base import SpeechService
from manim import logger

import pyaudio

from manim_recorder.recorder.gui.__gui__ import Recorder, QApplication, sys


class RecorderService(SpeechService):
    """Speech service that records from a microphone during rendering."""

    def __init__(
        self,
        recorder_service,
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
        self.recorder_service = recorder_service
        self.app = QApplication(sys.argv)
        self.recorder = Recorder(
            recorder_service=self.recorder_service
        )

        SpeechService.__init__(self, **kwargs)

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
                "format": self.recorder_service.format,
                "channels": self.recorder_service.channels,
                "rate": self.recorder_service.rate,
                "chunk": self.recorder_service.chunk,
            }
        }
        cached_result = self.get_cached_result(input_data, cache_dir, **kwargs)

        if cached_result is not None:
            return cached_result

        audio_path = self.get_audio_basename() + ".wav" if path is None else path

        # box = msg_box("Voiceover:\n\n" + text)
        # self.gui_recorder(str(Path(cache_dir) / audio_path), text)
        self.recorder.record(str(Path(cache_dir) / audio_path), text)
        self.app.exec()

        # self.recorder.record(str(Path(cache_dir) / audio_path), box)

        json_dict = {
            "input_data": input_data,
            "original_audio": audio_path
        }

        return json_dict
