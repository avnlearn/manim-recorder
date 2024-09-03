import sys
from manim_recorder.recorder.gui import Recorder
from PySide6.QtWidgets import QApplication
from manim_recorder.multimedia import Pyaudio_Recorder




if __name__ == "__main__":
    app = QApplication(sys.argv)
    recorder = Recorder()
    recorder.record(path=recorder.get_audio_basename() +
                    ".wav", msg="Start Recording")
    recorder.show()
    # audiorecoder.close()
    sys.exit(app.exec())
