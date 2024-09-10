import sys
import multiprocessing
from manim_recorder.recorder.gui import Recorder
from PySide6.QtWidgets import QApplication

# from PySide6.QtCore import QProcess, QThread
from manim_recorder.multimedia import PyAudio_


if __name__ == "__main__":
    app = QApplication(sys.argv)
    recorder = Recorder()
    recorder.show()
    sys.exit(app.exec())
