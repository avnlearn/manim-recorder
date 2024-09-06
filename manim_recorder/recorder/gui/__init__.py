from pathlib import Path
from manim_recorder.recorder.base import AudioService
# import multiprocessing
from manim_recorder.recorder.gui.__gui__ import Recorder, QApplication, sys


class RecorderService(AudioService):
    """Speech service that records from a microphone during rendering."""

    def __init__(self, **kwargs,):
        """Initialize the Audio service.
        Args:
        """
        self.app = QApplication(sys.argv)
        self.recorder = Recorder()
        AudioService.__init__(self, **kwargs)

    def generate_from_text(
        self, text: str, cache_dir: str = None, path: str = None, voice_id: int = None, svg_path: str | None = None, **kwargs
    ) -> dict:
        """"""

        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {
            'id': voice_id,
            "input_text": text,
            "MObject": str(svg_path)
        }
        cached_result = self.get_cached_result(
            input_data, cache_dir, voice_id=voice_id, **kwargs)

        if cached_result is not None:
            return cached_result

        audio_path = self.get_audio_basename() + ".wav" if path is None else path
        self.recorder.record(
            str(Path(cache_dir) / audio_path), text, voice_id, svg_path, **kwargs)
        self.app.exec()
        json_dict = {
            "input_data": input_data,
            "original_audio": audio_path
        }

        return json_dict
