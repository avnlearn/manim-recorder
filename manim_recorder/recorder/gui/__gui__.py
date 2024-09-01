import sys
import os
import wave
import datetime
import threading
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
    QLineEdit,
    QWidget,
    QMessageBox,
    QComboBox,
)
from PySide6.QtCore import Qt, QThread, Signal
import pyaudio


class Pyaudio_Recorder:
    def __init__(
        self,
        format: int = pyaudio.paInt16,
        channels: int = 1 if sys.platform == 'darwin' else 2,
        rate: int = 44100,
        chunk: int = 1024,
        device_index: int = None,
        callback_delay: float = 0.05,
        file_path: str = "output.wav",
        **kwargs
    ):
        self.format = format
        self.channels = channels
        self.rate = rate
        self.chunk = chunk
        self.device_index = device_index

        self.frames = []
        self.is_recording = False
        self.is_paused = False
        self.lock = threading.Lock()
        self.p = pyaudio.PyAudio()
        self.file_path = file_path
        self.playback_thread = None
        self.stop_playback_event = threading.Event()
        self.is_playing = False

    def set_device_index(self, device_index):
        try:
            self.p.get_device_info_by_host_api_device_index(0, device_index)
            return True
        except:
            print("Invalid device index. Please try again.")
            return False

    def set_channels(self, channels: int = None):
        if channels is None:
            channels = self.device_index
        try:
            print("Channels : ", channels)
            self.channels = self.p.get_device_info_by_host_api_device_index(
                0, channels).get("maxInputChannels")
            return True
        except:
            print("Invalid device index. Please try again.")
            return False

    def get_device_count(self):
        return self.p.get_host_api_info_by_index(0).get("deviceCount")

    def get_devices_name(self):
        return [
            self.p.get_device_info_by_host_api_device_index(0, i).get("name") for i in range(0, self.get_device_count()) if self.p.get_device_info_by_host_api_device_index(0, i).get("maxInputChannels") > 0
        ]

    def start_recording(self):
        self.frames = []
        self.is_recording = True
        self.is_paused = False
        self.thread = threading.Thread(target=self._record)
        self.thread.start()

    def _record(self):
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.rate,
                             input=True,
                             frames_per_buffer=self.chunk,
                             input_device_index=self.device_index)

        while self.is_recording:
            if not self.is_paused:
                data = stream.read(self.chunk)
                with self.lock:
                    self.frames.append(data)

        stream.stop_stream()
        stream.close()

    def pause_recording(self):
        self.is_paused = True

    def resume_recording(self):
        self.is_paused = False

    def stop_recording(self):
        self.is_recording = False
        self.thread.join()

    def save_recording(self):
        with wave.open(self.file_path, 'wb') as wf:
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.p.get_sample_size(pyaudio.paInt16))
            wf.setframerate(self.rate)
            wf.writeframes(b''.join(self.frames))

    def play_playback(self):
        if not self.frames:
            return False
        self.is_playing = True
        self.stop_playback_event.clear()  # Clear the stop event
        self.playback_thread = threading.Thread(target=self._playback)
        self.playback_thread.start()

    def _playback(self):
        stream = self.p.open(format=self.format,
                             channels=self.channels,
                             rate=self.rate,
                             output=True)

        for data in self.frames:
            if self.stop_playback_event.is_set():
                break
            stream.write(data)

        stream.stop_stream()
        stream.close()

    def stop_playback(self):
        self.is_playing = False
        self.stop_playback_event.set()  # Signal to stop playback
        if self.playback_thread is not None:
            self.playback_thread.join()  # Wait for the playback thread to finish

    def close(self):
        self.p.terminate()

    def set_filepath(self, path: str):
        self.file_path = str(path)

    def __str__(self):
        if isinstance(self.file_path):
            if os.path.exists(str(self.file_path)):
                return str(self.file_path)
        return ""


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

        # Populate the combo box with available audio input devices
        self.populate_device_list()

    def initUI(self):
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 300, 250)
        layout = QVBoxLayout()

        # Device Index List
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.set_device_index)
        layout.addWidget(self.device_combo)

        # Message
        self.massage_label = QLabel("Start", self)
        self.massage_label.setAlignment(Qt.AlignCenter)
        self.massage_label.setWordWrap(True)
        layout.addWidget(self.massage_label)

        # Recording Button
        self.recording_button = QPushButton("Start Recording")
        self.recording_button.clicked.connect(self.toggle_recording)
        layout.addWidget(self.recording_button)

        # Playback Button
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

    def populate_device_list(self):
        self.device_combo.addItems(self.recorder_service.get_devices_name())

    def set_device_index(self, index):
        self.status_label.setText("Device: {}".format(index))
        self.device_index = self.device_combo.itemData(index)

    def toggle_recording(self):
        if not self.recorder_service.is_recording:
            self.start_recording()
            self.playback_button.setDisabled(True)
            self.save_button.setDisabled(True)
        else:
            self.stop_recording()
            self.playback_button.setDisabled(False)
            self.save_button.setDisabled(False)

    def start_recording(self):
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
            self.close()
        else:
            self.show_message("No Recording", "Plase before save file")

    def show_message(self, title, message):
        msg_box = QMessageBox(self)
        msg_box.setWindowTitle(title)
        msg_box.setText(message)
        # You can change the icon type
        msg_box.setIcon(QMessageBox.Information)
        msg_box.setStandardButtons(QMessageBox.Ok)  # Add an OK button
        msg_box.exec()  # Show the message box

    def closeEvent(self, event):
        # Save answers to a file when the window is closed
        self.save_audio()
        event.accept()  # Accept the event to close the window

    def record(self, path: str, msg: str = None):
        self.recorder_service.set_filepath(path)
        self.massage_label.setText(msg)
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
