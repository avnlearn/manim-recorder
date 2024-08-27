from math import ceil
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, Generator
import re

from manim import Scene, config
from manim_recorder.recorder.base import SpeechService
from manim_recorder.tracker import VoiceoverTracker
from manim_recorder.helper import chunks


class RecorderScene(Scene):
    """A scene class that can be used to add voiceover to a scene."""

    speech_service: SpeechService
    current_tracker: Optional[VoiceoverTracker]
    create_subcaption: bool
    create_script: bool
    voice_id: int = -1

    def set_speech_service(
        self,
        speech_service: SpeechService,
        create_subcaption: bool = True,
    ) -> None:
        """Sets the speech service to be used for the voiceover. This method
        should be called before adding any voiceover to the scene.

        Args:
            speech_service (SpeechService): The speech service to be used.
            create_subcaption (bool, optional): Whether to create subcaptions for the scene. Defaults to True.
        """
        if hasattr(speech_service, "default_cache_dir"):
            if speech_service.default_cache_dir:
                speech_service.recording_cache_dir(
                    Path(config.media_dir) / Path("recordings") / Path(self.__class__.__name__))
        self.speech_service = speech_service
        self.current_tracker = None
        self.create_subcaption = create_subcaption

    def add_voiceover_text(
        self,
        text: str,
        subcaption: Optional[str] = None,
        max_subcaption_len: int = 70,
        subcaption_buff: float = 0.1,
        **kwargs,
    ) -> VoiceoverTracker:
        """Adds voiceover to the scene.

        Args:
            text (str): The text to be spoken.
            subcaption (Optional[str], optional): Alternative subcaption text. If not specified, `text` is chosen as the subcaption. Defaults to None.
            max_subcaption_len (int, optional): Maximum number of characters for a subcaption. Subcaptions that are longer are split into chunks that are smaller than `max_subcaption_len`. Defaults to 70.
            subcaption_buff (float, optional): The duration between split subcaption chunks in seconds. Defaults to 0.1.

        Returns:
            VoiceoverTracker: The tracker object for the voiceover.
        """
        if not hasattr(self, "speech_service"):
            raise Exception(
                "You need to call init_voiceover() before adding a voiceover."
            )

        dict_ = self.speech_service._wrap_generate_from_text(
            text=text, voice_id=self.voice_id, **kwargs)
        tracker = VoiceoverTracker(
            self, dict_, self.speech_service.cache_dir, self.voice_id)

        self.renderer.file_writer.add_sound(
            str(Path(self.speech_service.cache_dir) / dict_["final_audio"]), self.renderer.time + 0, None, **kwargs)
        self.current_tracker = tracker

        if self.create_subcaption:
            if subcaption is None:
                # Remove placeholders
                subcaption = re.sub(r"<[^<>]+/>", "", text)

            self.add_wrapped_subcaption(
                subcaption,
                tracker.duration,
                subcaption_buff=subcaption_buff,
                max_subcaption_len=max_subcaption_len,
            )

        return tracker

    def add_wrapped_subcaption(
        self,
        subcaption: str,
        duration: float,
        subcaption_buff: float = 0.1,
        max_subcaption_len: int = 70,
    ) -> None:
        """Adds a subcaption to the scene. If the subcaption is longer than `max_subcaption_len`, it is split into chunks that are smaller than `max_subcaption_len`.

        Args:
            subcaption (str): The subcaption text.
            duration (float): The duration of the subcaption in seconds.
            max_subcaption_len (int, optional): Maximum number of characters for a subcaption. Subcaptions that are longer are split into chunks that are smaller than `max_subcaption_len`. Defaults to 70.
            subcaption_buff (float, optional): The duration between split subcaption chunks in seconds. Defaults to 0.1.
        """
        subcaption = " ".join(subcaption.split())
        n_chunk = ceil(len(subcaption) / max_subcaption_len)
        tokens = subcaption.split(" ")
        chunk_len = ceil(len(tokens) / n_chunk)
        chunks_ = list(chunks(tokens, chunk_len))
        try:
            assert len(chunks_) == n_chunk or len(chunks_) == n_chunk - 1
        except AssertionError:
            import ipdb

            ipdb.set_trace()

        subcaptions = [" ".join(i) for i in chunks_]
        subcaption_weights = [
            len(subcaption) / len("".join(subcaptions)) for subcaption in subcaptions
        ]

        current_offset = 0
        for idx, subcaption in enumerate(subcaptions):
            chunk_duration = duration * subcaption_weights[idx]
            self.add_subcaption(
                subcaption,
                duration=max(chunk_duration - subcaption_buff, 0),
                offset=current_offset,
            )
            current_offset += chunk_duration

    def wait_for_voiceover(self) -> None:
        """Waits for the voiceover to finish."""
        if not hasattr(self, "current_tracker"):
            return
        if self.current_tracker is None:
            return

        self.safe_wait(self.current_tracker.get_remaining_duration())

    def safe_wait(self, duration: float) -> None:
        """Waits for a given duration. If the duration is less than one frame, it waits for one frame.

        Args:
            duration (float): The duration to wait for in seconds.
        """
        if duration > 1 / config["frame_rate"]:
            self.wait(duration)

    @contextmanager
    def voiceover(
        self, text: str = None, **kwargs
    ) -> Generator[VoiceoverTracker, None, None]:
        """The main function to be used for adding voiceover to a scene.

        Args:
            text (str, optional): The text to be spoken. Defaults to None.
        Yields:
            Generator[VoiceoverTracker, None, None]: The voiceover tracker object.
        """
        if text is None:
            raise ValueError(
                "Please specify either a voiceover text string.")

        try:
            # Increment voice_id after adding a new voiceover
            self.voice_id += 1
            yield self.add_voiceover_text(text, **kwargs)
        finally:
            self.wait_for_voiceover()
