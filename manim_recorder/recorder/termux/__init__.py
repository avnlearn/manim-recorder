from pathlib import Path
from manim_recorder.helper import msg_box
from manim_recorder.recorder.base import SpeechService
from manim import logger
from manim_recorder.recorder.termux.cli import Recorder


class RecorderService(SpeechService):
    """Speech service that records from a microphone during rendering."""

    def __init__(
        self,
        encoder: str = "acc",
        channel_count: int = 1,
        sampling_rate: int = 44100,
        trim_silence_threshold: float = -40.0,
        trim_buffer_start: int = 200,
        trim_buffer_end: int = 200,
        callback_delay: float = 0.05,
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

        self.recorder = Recorder(
            encoder=encoder,
            channel_count=channel_count,
            sampling_rate=sampling_rate,
            trim_silence_threshold=trim_silence_threshold,
            trim_buffer_start=trim_buffer_start,
            trim_buffer_end=trim_buffer_end
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
                "encoder": self.recorder.encoder,
                "channel_count": self.recorder.channel_count,
                "sampling_rate": self.recorder.sampling_rate,
            },
        }
        cached_result = self.get_cached_result(input_data, cache_dir)
        if cached_result is not None:
            return cached_result

        audio_path = self.get_audio_basename() + ".m4a" if path is None else path

        box = msg_box("Voiceover:\n\n" + text)
        self.recorder.record(str(Path(cache_dir) / audio_path), box)
        json_dict = {
            "input_text": text,
            "input_data": input_data,
            "original_audio": audio_path,
        }

        return json_dict
