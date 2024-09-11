from pathlib import Path
import sys
import logging
from manim_recorder.recorder.base import AudioService
from manim_recorder.recorder.gui.__gui__ import Recorder, QApplication, sys
from manim_recorder.helper import get_audio_basename
from PySide6.QtCore import Signal, QObject, QEventLoop


class Communicate(QObject):
    recorder_data = Signal(str, str, int, str)  # Ensure this matches the emitted signal
    accept = Signal(str)


class RecorderService(AudioService):
    """Speech service that records from a microphone during rendering."""

    def __init__(
        self,
        **kwargs,
    ):
        """Initialize the Audio service.
        Args:
        """
        AudioService.__init__(self, **kwargs)
        self.app = QApplication(sys.argv)
        self.communicator = Communicate()
        self.communicator.accept.connect(self.recorder_complated)
        self.recorder = Recorder(communicator=self.communicator)
        # self.recorder.show()
        self.loop = QEventLoop()

    def generate_from_text(
        self,
        text: str,
        cache_dir: str = None,
        path: str = None,
        voice_id: int = None,
        mobject: str | None = None,
        **kwargs,
    ) -> dict:
        """"""

        if cache_dir is None:
            cache_dir = self.cache_dir

        input_data = {"id": voice_id, "input_text": text, "MObject": str(mobject)}
        cached_result = self.get_cached_result(
            input_data, cache_dir, voice_id=voice_id, **kwargs
        )

        if cached_result is not None:
            return cached_result

        if not self.recorder.isVisible():
            self.recorder.show()

        audio_path = get_audio_basename() + ".wav" if path is None else path

        self.communicator.recorder_data.emit(
            str(Path(cache_dir) / audio_path), text, voice_id, str(mobject)
        )

        self.loop = QEventLoop()
        self.communicator.accept.connect(self.loop.quit)
        self.loop.exec()

        json_dict = {"input_data": input_data, "original_audio": audio_path}

        return json_dict

    def recorder_complated(self, message):
        logging.info(f"Save Audio File : {message}")

    def app_exec(self):
        self.recorder.close()
        self.loop.exit()
        sys.exit(self.app.exec)
        QApplication.exit()
