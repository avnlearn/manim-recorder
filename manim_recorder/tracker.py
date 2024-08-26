from pathlib import Path
from manim import logger
from manim import Scene
from manim_recorder.modify_audio import get_duration


AUDIO_OFFSET_RESOLUTION = 10_000_000


class VoiceoverTracker:
    """Class to track the progress of a voiceover in a scene."""

    def __init__(self, scene: Scene, data: dict, cache_dir: str, voice_id:int):
        """Initializes a VoiceoverTracker object.

        Args:
            scene (Scene): The scene to which the voiceover belongs.
            path (str): The path to the JSON file containing the voiceover data.
        """
        self.scene = scene
        self.data = data
        self.cache_dir = cache_dir
        self.voice_id = voice_id
        self.duration = get_duration(
            Path(cache_dir) / self.data["final_audio"])
        last_t = scene.renderer.time
        if last_t is None:
            last_t = 0
        self.start_t = last_t
        self.end_t = last_t + self.duration

    def get_remaining_duration(self, buff: float = 0.0) -> float:
        """Returns the remaining duration of the voiceover.

        Args:
            buff (float, optional): A buffer to add to the remaining duration. Defaults to 0.

        Returns:
            int: The remaining duration of the voiceover in seconds.
        """
        # result= max(self.end_t - self.scene.last_t, 0)
        result = max(self.end_t - self.scene.renderer.time + buff, 0)
        # print(result)
        return result
