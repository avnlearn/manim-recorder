import sys
import os
import datetime
import threading
import multiprocessing
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QWidget,
    QMessageBox,
    QComboBox, QStyle
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer
from manim_recorder.multimedia import Pyaudio_Recorder


class Recorder(QMainWindow):
    def __init__(
        self,
        msg: str = "Start",
        recorder_service=Pyaudio_Recorder(),
        parent=None,
        **kwargs
    ):
        super().__init__(parent)
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

        # Message
        self.massage_label = QLabel("Message", self)
        self.massage_label.setAlignment(Qt.AlignCenter)
        self.massage_label.setWordWrap(True)
        layout.addWidget(self.massage_label)
        self.massage_label.setStyleSheet("color:orange;")
        # self.massage_label.setStyleSheet("font-size: 10px;")

        # Timer
        self.recording_timer_label = QLabel("00:00:00")
        self.recording_timer_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.recording_timer_label)
        self.recording_timer_label.setStyleSheet("font-size: 30px;")
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)

        # Recording Button
        self.recording_button = QPushButton("Start Recording")
        self.recording_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.recording_button)
        # Get the theme icon for the standard "SP_MediaPlay" (play button) icon
        icon = self.style().standardIcon(QStyle.SP_MediaPlay)
        self.recording_button.setIcon(icon)

        # Playback Button
        self.duration_label = QLabel("00:00:00")
        self.duration_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.duration_label)
        self.duration_label.setStyleSheet("font-size: 30px;")

        self.playback_button = QPushButton("Play")
        self.playback_button.clicked.connect(self.toggle_playback)
        layout.addWidget(self.playback_button)
        self.playback_button.setDisabled(True)

        # Accept Button > Save
        self.save_button = QPushButton("Accept")
        self.save_button.clicked.connect(self.save_audio)
        layout.addWidget(self.save_button)
        self.save_button.setDisabled(True)

        # Status Button
        self.status_label = QLabel("Status: Idle")
        layout.addWidget(self.status_label)

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

    def populate_device_list(self):
        self.device_combo.addItems(self.recorder_service.get_devices_name())

    def set_device_index(self, index):
        self.status_label.setText("Device: {}".format(index))
        self.device_index = self.device_combo.itemData(index)

    def start_timer(self):
        self.timer.start(100)  # Timer will trigger every 1000 ms (1 second)

    def stop_timer(self):
        self.timer.stop()

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
        self.status_label.setText("Status: Recording...")
        self.recorder_service.set_device_index(self.device_index)
        self.recorder_service.set_channels(self.device_index)
        self.recorder_service.start_recording()

    def stop_recording(self):
        self.recording_button.setText("re-Recording")
        self.recording_button.setStyleSheet(
            "background-color: black; color: white;")
        self.status_label.setText("Status: Stopped Recording")
        self.recorder_service.stop_recording()
        # self.save_audio()

    def toggle_playback(self):
        if not self.recorder_service.is_playing:
            self.play_playback()
            self.recording_button.setDisabled(True)
        else:
            self.stop_playback()
            self.recording_button.setDisabled(False)

    def play_playback(self):
        self.playback_button.setText("Stop Playback")
        self.playback_button.setStyleSheet(
            "background-color: red; color: white;")
        self.status_label.setText("Status: Started Recording Listening ...")
        self.recorder_service.play_playback()

    def stop_playback(self):
        self.playback_button.setText("Start Playback")
        self.playback_button.setStyleSheet("")
        self.status_label.setText("Status: Stopped Recording Listening ...")
        self.recorder_service.stop_playback()

    def get_audio_basename(self) -> str:
        now = datetime.datetime.now()
        return "Voice_{}".format(now.strftime("%d%m%Y_%H%M%S"))

    def save_audio(self):
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

    def record(self, path: str, msg: str = None):
        self.File_Saved = False
        self.recorder_service.set_filepath(path)
        self.massage_label.setText(msg)
        self.reset_timer()
        self.duration_label.setText("")
        self.recording_button.setText("Start Recording")
        self.recording_button.setStyleSheet("")
        self.status_label.setText("Status: None")
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
