from abc import ABC, abstractmethod
import os
import json
import sys
from pathlib import Path
import datetime
from manim import config, logger
from manim_recorder.defaults import (
    DEFAULT_VOICEOVER_CACHE_DIR,
    DEFAULT_VOICEOVER_CACHE_JSON_FILENAME,
)
from manim_recorder.modify_audio import adjust_speed
from manim_recorder.helper import append_to_json_file


class SpeechService(ABC):
    """Abstract base class for a speech service."""

    def __init__(
        self,
        global_speed: float = 1.00,
        cache_dir: Path = None,
        **kwargs
    ):
        """
        Args:
            global_speed (float, optional): The speed at which to play the audio.
                Defaults to 1.00.
            cache_dir (str, optional): The directory to save the audio
                files to. Defaults to ``voiceovers/``.
        """
        self.global_speed = global_speed
        self.default_cache_dir = True
        self.cache_dir = self.recording_cache_dir(cache_dir)
        self.additional_kwargs = kwargs

    def recording_cache_dir(self, cache_dir: Path):
        if cache_dir is not None:
            self.cache_dir = cache_dir
            self.default_cache_dir = False
        else:
            self.cache_dir = Path(config.media_dir) / \
                DEFAULT_VOICEOVER_CACHE_DIR
            self.default_cache_dir = True

        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

        return self.cache_dir

    def _wrap_generate_from_text(self, text: str, path: str = None, **kwargs) -> dict:
        # Replace newlines with lines, reduce multiple consecutive spaces to single
        text = " ".join(text.split())

        dict_ = self.generate_from_text(
            text, cache_dir=None, path=path, **kwargs)

        original_audio = dict_["original_audio"]

        # Audio callback
        self.audio_callback(original_audio, dict_, **kwargs)

        if self.global_speed != 1:
            split_path = os.path.splitext(original_audio)
            adjusted_path = split_path[0] + "_adjusted" + split_path[1]

            adjust_speed(
                Path(self.cache_dir) / dict_["original_audio"],
                Path(self.cache_dir) / adjusted_path,
                self.global_speed,
            )
            dict_["final_audio"] = adjusted_path
        else:
            dict_["final_audio"] = dict_["original_audio"]

        append_to_json_file(
            Path(self.cache_dir) / DEFAULT_VOICEOVER_CACHE_JSON_FILENAME, dict_, **kwargs
        )

        return dict_

    def get_audio_basename(self) -> str:
        now = datetime.datetime.now()
        return "Voice_{}".format(now.strftime('%d%m%Y_%H%M%S'))

    @abstractmethod
    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None
    ) -> dict:
        """Implement this method for each speech service. Refer to `AzureService` for an example.

        Args:
            text (str): The text to synthesize speech from.
            cache_dir (str, optional): The output directory to save the audio file and data to. Defaults to None.
            path (str, optional): The path to save the audio file to. Defaults to None.

        Returns:
            dict: Output data dictionary. TODO: Define the format.
        """
        raise NotImplementedError

    def get_cached_result(self, input_data, cache_dir, voice_id: int = -1, **kwargs):
        json_path = os.path.join(
            cache_dir / DEFAULT_VOICEOVER_CACHE_JSON_FILENAME)

        if os.path.exists(json_path):
            json_data = json.load(open(json_path, "r"))
            if voice_id > -1 and 0 <= voice_id < len(json_data):
                if json_data[voice_id]["input_data"] == input_data:
                    return json_data[voice_id]
            else:
                return None

            for entry in json_data:
                if entry["input_data"] == input_data:
                    return entry
        return None

    def audio_callback(self, audio_path: str, data: dict, **kwargs):
        """Callback function for when the audio file is ready.
        Override this method to do something with the audio file, e.g. noise reduction.

        Args:
            audio_path (str): The path to the audio file.
            data (dict): The data dictionary.
        """
        pass
