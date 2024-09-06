import sys
import os
import datetime
import threading
import multiprocessing
from PySide6.QtGui import QIcon, QPalette
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QWidget,
    QMessageBox,
    QComboBox, QStyle,
    QHBoxLayout, QStatusBar,
    QSizePolicy
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer

from manim_recorder.multimedia import Pyaudio_Recorder
from manim_recorder.recorder.gui.util import Run_Audacity


class Recorder(QMainWindow):
    def __init__(
        self,
        msg: str = "Start",
        recorder_service=Pyaudio_Recorder(),
        parent=None,
        **kwargs
    ):
        super().__init__(parent)
        self.DEFAULT_SVG = os.path.join(
            os.path.dirname(__file__), "assets/Mic.svg")
        self.initUI()
        self.recorder_service = recorder_service
        self.msg = msg
        self.File_Saved = False
        self.populate_device_list()

    def initUI(self):
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 500, 400)
        self.center()
        self.setWindowFlags(self.windowFlags() | Qt.WindowStaysOnTopHint)
        layout = QVBoxLayout()

        # Device Index List
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.set_device_index)
        layout.addWidget(self.device_combo)

        # Script

        self.speech_script_label = QLabel("Speech Script", self)
        self.speech_script_label.setAlignment(Qt.AlignLeft)
        self.speech_script_label.setWordWrap(True)
        layout.addWidget(self.speech_script_label)
        self.speech_script_label.setStyleSheet(
            "font-weight:bold; font-size: 20px;")

        self.message_object = QSvgWidget()
        

        # Set size policy to allow the widget to expand
        self.message_object.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.setSvg_Size(self.DEFAULT_SVG)
        self.message_object.load(self.DEFAULT_SVG)
        layout.addWidget(self.message_object, alignment=Qt.AlignCenter)

        # Message
        self.massage_label = QLabel("Message", self)
        self.massage_label.setAlignment(Qt.AlignCenter)
        self.massage_label.setWordWrap(True)
        layout.addWidget(self.massage_label)
        self.massage_label.setStyleSheet("color:orange;")
        self.massage_label.setStyleSheet("font-size: 15px;")

        rec_layout = QHBoxLayout()
        # Recording Button
        self.recording_button = QPushButton("Start Recording")
        self.recording_button.setShortcut("r")
        self.recording_button.clicked.connect(self.toggle_recording)
        rec_layout.addWidget(self.recording_button)
        # Get the theme icon for the standard "SP_MediaPlay" (play button) icon
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.recording_button.setIcon(icon)

        # Recording Timer
        self.recording_timer_label = QLabel("00:00:00")
        self.recording_timer_label.setAlignment(Qt.AlignCenter)
        rec_layout.addWidget(self.recording_timer_label)
        self.recording_timer_label.setStyleSheet("font-size: 30px;")
        self.recording_timer = QTimer()
        self.recording_timer.timeout.connect(self.update_time)
        layout.addLayout(rec_layout)

        m_layout = QHBoxLayout()

        # Playback Button
        self.playback_button = QPushButton("Play")
        self.playback_button.clicked.connect(self.toggle_playback)
        m_layout.addWidget(self.playback_button)
        self.playback_button.setDisabled(True)

        # Player Timer
        self.duration_label = QLabel("00:00:00")
        self.duration_label.setAlignment(Qt.AlignCenter)
        m_layout.addWidget(self.duration_label)
        self.duration_label.setStyleSheet("font-size: 30px;")

        # Accept Button > Save
        self.save_button = QPushButton("Accept")
        self.save_button.clicked.connect(self.save_audio)
        m_layout.addWidget(self.save_button)
        self.save_button.setDisabled(True)
        layout.addLayout(m_layout)
        # Run Audacity

        # h_layout = QHBoxLayout()
        # self.audacity_button = QPushButton("Run Audacity")
        # self.audacity_button.clicked.connect(lambda: Run_Audacity(self.recorder_service.__str__()))
        # h_layout.addWidget(self.audacity_button)
        # layout.addLayout(h_layout)
        # Status Button
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)

    def center(self):
        # Get the screen geometry using QScreen
        screen_geometry = self.screen().availableGeometry()
        # Get the window geometry
        window_geometry = self.geometry()

        # Calculate the center position
        x = (screen_geometry.width() - window_geometry.width()) // 2
        y = (screen_geometry.height() - window_geometry.height()) // 2

        # Move the window to the center
        self.move(x, y)

    def setSvg_Size(self, svg_path):
        renderer = QSvgRenderer(svg_path)
        
        original_size = renderer.defaultSize()
        # original_size.setHeight(original_size.height() * 20)
        # original_size.setWidth(original_size.width() * 20)
        # Set the size of the QSvgWidget to the original size
        self.message_object.setFixedSize(original_size)

    def populate_device_list(self):
        self.device_combo.addItems(self.recorder_service.get_devices_name())

    def set_device_index(self, index):
        self.status_bar.showMessage("Device: {}".format(index))
        self.device_index = self.device_combo.itemData(index)

    def start_timer(self):
        # Timer will trigger every 1000 ms (1 second)
        self.recording_timer.start(100)

    def stop_timer(self):
        self.recording_timer.stop()

    def reset_timer(self):
        self.stop_timer()  # Stop the timer if it's running
        self.recording_timer_label.setText("00:00:00")  # Reset display

    def update_time(self):
        self.recording_timer_label.setText(
            self.recorder_service.format_duration())

    def toggle_recording(self):
        if not self.recorder_service.is_recording:
            self.start_recording()
            self.playback_button.setDisabled(True)
            self.save_button.setDisabled(True)
            self.start_timer()
            if self.recorder_service.is_playing:
                self.recorder_service.stop_playback()
        else:
            self.stop_recording()
            self.playback_button.setDisabled(False)
            self.save_button.setDisabled(False)
            self.duration_label.setText(
                self.recorder_service.format_duration())
            self.stop_timer()

    def start_recording(self):
        self.recording_timer_label.setText("00:00:00")
        self.recording_button.setText("Stop Recording")
        self.recording_button.setStyleSheet(
            "background-color: red; color: white;")
        self.status_bar.showMessage("Status : Recording ...")
        self.recorder_service.set_device_index(self.device_index)
        self.recorder_service.set_channels(self.device_index)
        self.recorder_service.start_recording()

    def stop_recording(self):
        self.recording_button.setText("re-Recording")
        self.recording_button.setStyleSheet(
            "background-color: black; color: white;")
        self.status_bar.showMessage("Status: Re-recording")
        self.recorder_service.stop_recording()

    def toggle_playback(self):
        if not self.recorder_service.is_playing and not self.recorder_service.is_recording:
            self.play_playback()
            self.recording_button.setDisabled(True)
        else:
            self.stop_playback()
            self.recording_button.setDisabled(False)

    def play_playback(self):
        self.playback_button.setText("Stop Playback")
        self.playback_button.setStyleSheet(
            "background-color: red; color: white;")
        self.status_bar.showMessage("Status: Started Recording Listening ...")
        self.recorder_service.play_playback()

    def stop_playback(self):
        self.playback_button.setText("Start Playback")
        self.playback_button.setStyleSheet("")
        self.status_bar.showMessage("Status: Stopped Recording Listening ...")
        self.recorder_service.stop_playback()

    def get_audio_basename(self) -> str:
        now = datetime.datetime.now()
        return "Voice_{}".format(now.strftime("%d%m%Y_%H%M%S"))

    def save_audio(self):
        if self.recorder_service.is_recording:
            self.recorder_service.stop_recording()
        if self.recorder_service.is_playing:
            self.recorder_service.stop_playback()
        if self.recorder_service.frames:
            self.recorder_service.save_recording()
            self.File_Saved = True
            self.close()
        else:
            self.show_message("No Recording", "Plase before save file")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        # You can change the icon type
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
        return msg_box.exec()  # Show the message box

    def closeEvent(self, event):
        if not self.File_Saved:
            if self.show_message("Confirmation", "Do you save audio file?") == QMessageBox.Yes:
                self.save_audio()
        # self.recorder_service.frames = []
        event.accept()  # Accept the event to close the window

    def resetUI(self):
        self.File_Saved = False
        self.massage_label.setText("Message")
        self.speech_script_label.setText("Speech Script")
        self.duration_label.setText("")
        self.reset_timer()
        self.recording_button.setText("Start Recording")
        self.recording_button.setStyleSheet("")
        self.status_bar.clearMessage()

        # self.message_object.load(self.DEFAULT_SVG)
        # self.setSvg_Size(self.DEFAULT_SVG)

    def record(self, path: str = None, msg: str = None, voice_id: int = None, mobject_path: any = None, **kwargs):
        self.resetUI()
        if path is not None:
            self.recorder_service.set_filepath(path)
        if mobject_path is not None:
            mobject_path = str(mobject_path)
            self.message_object.setStyleSheet("background-color: white; padding: 20px;")
            self.message_object.load(mobject_path)
            self.setSvg_Size(mobject_path)

        if msg is not None:
            self.massage_label.setText(msg)
        if voice_id is not None:
            self.speech_script_label.setText("Sound ID : {}".format(voice_id))

        self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    audiorecoder = Pyaudio_Recorder()
    recorder = Recorder(audiorecoder)
    recorder.record(path=recorder.get_audio_basename() +
                    ".wav", msg="Start Recording")
    recorder.show()
    # audiorecoder.close()
    sys.exit(app.exec())
