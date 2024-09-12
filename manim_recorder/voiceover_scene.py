"""
"""

import re
import os
from typing import override
from pathlib import Path
from math import ceil
from contextlib import contextmanager
from typing import Optional, Generator
from manim import Scene, config, Mobject, logger
from manim.utils.file_ops import open_media_file
from manim_recorder.recorder.base import AudioService
from manim_recorder.tracker import SoundTracker
from manim_recorder.multimedia import chunks
from manim_recorder.helper import text_and_mobject


class RecorderScene(Scene):
    """A scene class that can be used to add sound to a scene."""

    audio_service: AudioService
    current_tracker: Optional[SoundTracker]
    create_subcaption: bool
    create_script: bool
    voice_id: int = -1

    def set_audio_service(
        self,
        audio_service: AudioService,
        create_subcaption: bool | None = True,
        cache_dir_delete: bool = False,
    ) -> None:
        """Sets the Audio service to be used for the sound. This method
        should be called before adding any sound to the scene.

        Args:
            audio_service (AudioService): The audio service to be used.
            create_subcaption (bool, optional): Whether to create subcaptions for the scene. Defaults to True.
        """
        if hasattr(audio_service, "default_cache_dir"):
            if audio_service.default_cache_dir:
                audio_service.recording_cache_dir(
                    os.path.join(str(config.media_dir), "sounds", str(self)),
                    cache_dir_delete,
                )
        self.audio_service = audio_service
        self.current_tracker = None
        self.create_subcaption = create_subcaption

    def add_voiceover_text(
        self,
        text: str,
        subcaption: Optional[str] = None,
        max_subcaption_len: int = 70,
        subcaption_buff: float = 0.1,
        gain_to_background: float | None = None,
        **kwargs,
    ) -> SoundTracker:
        """Adds sound to the scene.

        Args:
            text (str): The text to be spoken.
            subcaption (Optional[str], optional): Alternative subcaption text. If not specified, `text` is chosen as the subcaption. Defaults to None.
            max_subcaption_len (int, optional): Maximum number of characters for a subcaption. Subcaptions that are longer are split into chunks that are smaller than `max_subcaption_len`. Defaults to 70.
            subcaption_buff (float, optional): The duration between split subcaption chunks in seconds. Defaults to 0.1.

        Returns:
            SoundTracker: The tracker object for the sound.
        """
        if not hasattr(self, "audio_service"):
            raise Exception("You need to call init_sound() before adding a sound.")

        dict_ = self.audio_service._wrap_generate_from_text(
            text=text, voice_id=self.voice_id, **kwargs
        )
        tracker = SoundTracker(self, dict_, self.audio_service.cache_dir, self.voice_id)

        audio_file_path = str(Path(self.audio_service.cache_dir) / dict_["final_audio"])

        if os.path.exists(audio_file_path):
            self.renderer.file_writer.add_sound(
                str(Path(self.audio_service.cache_dir) / dict_["final_audio"]),
                self.renderer.time + 0,
                None,
            )
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

    def say_to_wait(
        self,
        text: str | None = None,
        mobject: Mobject | None = None,
        *args,
        **kwargs,
    ) -> None:
        if text is None and len(args) == 0:
            text = "Say {}".format(self.voice_id)

        with self.voiceover(text=text, mobject=mobject) as tracker:
            if len(args):
                self.play(*args, run_time=tracker.duration)
            else:
                self.safe_wait(tracker.duration)

    def say_to_play(
        self,
        *mobject_args,
        text: str | None = None,
        mobject: Mobject | None = None,
        **kwargs,
    ):

        with self.voiceover(text=text, mobject=mobject) as tracker:
            self.play(*mobject_args, run_time=tracker.duration)

    def wait_for_voiceover(self) -> None:
        """Waits for the sound to finish."""
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
        self, text: str | None = None, mobject: Mobject | None = None, **kwargs
    ) -> Generator[SoundTracker, None, None]:
        """The main function to be used for adding sound to a scene.

        Args:
            text (str, optional): The text to be spoken. Defaults to None.
            mobject (str, optional) : The Mobject to be spoken. Default to None
        Yields:
            Generator[SoundTracker, None, None]: The sound tracker object.
        """
        if text is None and mobject is None:
            raise ValueError(
                "Please specify either a sound text string and mobject path."
            )
        else:
            text, mobject = text_and_mobject(text, mobject)

        try:
            # Increment voice_id after adding a new sound
            self.voice_id += 1
            yield self.add_voiceover_text(text, mobject=mobject, **kwargs)
        finally:
            self.wait_for_voiceover()

    @override
    def render(self, preview: bool = False):
        """
        Renders this Scene.

        Parameters
        ---------
        preview
            If true, opens scene in a file viewer.
        """
        self.setup()
        try:
            self.construct()
        except EndSceneEarlyException:
            pass
        except RerunSceneException as e:
            self.remove(*self.mobjects)
            self.renderer.clear_screen()
            self.renderer.num_plays = 0
            return True
        self.tear_down()
        # We have to reset these settings in case of multiple renders.
        self.renderer.scene_finished(self)

        # Show info only if animations are rendered or to get image
        if (
            self.renderer.num_plays
            or config["format"] == "png"
            or config["save_last_frame"]
        ):
            logger.info(
                f"Rendered {str(self)}\nPlayed {self.renderer.num_plays} animations",
            )

        # If preview open up the render after rendering.
        if preview:
            config["preview"] = True

        if config["preview"] or config["show_in_file_browser"]:
            open_media_file(self.renderer.file_writer)

        if hasattr(self, "audio_service"):
            if hasattr(self.audio_service, "app_exec"):
                self.audio_service.app_exec()
