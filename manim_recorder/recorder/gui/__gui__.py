"""
GUI Recorder
"""

import sys
import datetime
from PySide6.QtGui import QIcon, QPalette, QColor, QShortcut, QKeySequence
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
    QStyle,
    QHBoxLayout,
    QStatusBar,
    QSizePolicy,
    QProgressBar,
)
import numpy as np
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
import pyqtgraph as pg
from manim_recorder.multimedia import PyAudio_
from manim_recorder.recorder.gui.util import Run_Audacity
from manim_recorder.recorder.gui.ui import (
    create_label,
    Create_Button,
    WindowCenter,
    SVG_Viewer,
    SVG_Icon,
    show_message,
)


class Recorder(QMainWindow):
    """
    A class to represent an audio recorder application using PySide6.

    Attributes:
        recorder_service: An instance of the audio recording service.
        msg: A message to display in the UI.
        File_Saved: A boolean indicating if the audio file has been saved.
    """

    def __init__(
        self,
        msg: str = "Start",
        recorder_service=PyAudio_(),
        parent=None,
        **kwargs,
    ):
        """
        Initializes the Recorder application.

        Args:
            msg (str): The initial message to display.
            recorder_service: An instance of the audio recording service.
            parent: The parent widget.
            **kwargs: Additional keyword arguments.
        """
        super().__init__(parent)
        self.initUI()
        self.recorder_service = recorder_service
        self.msg = msg
        self.File_Saved = False
        self.populate_device_list()
        self.waveform_chart_timer = pg.QtCore.QTimer()
        self.waveform_chart_timer.timeout.connect(self.update_plot)
        self.progress_timer = QTimer(self)
        self.progress_timer.timeout.connect(self.update_progress_bar)

    def initUI(self):
        """Initializes the user interface components."""
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 500, 400)
        WindowCenter(self, onTop=True)

        layout = QVBoxLayout()

        # Device Index List
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.set_device_index)
        layout.addWidget(self.device_combo)

        # Speech Script Section
        message_layout = QVBoxLayout()

        self.message_object = SVG_Viewer(svg_file=SVG_Icon["MIC"])

        message_layout.addWidget(
            self.message_object, alignment=Qt.AlignCenter, stretch=1
        )

        # Message Display
        self.message_label = create_label(
            "Message", "color:orange; font-size: 15px", align="c", wordwrap=True
        )
        message_layout.addWidget(self.message_label)
        layout.addLayout(message_layout)

        # Waveform Chart
        self.plot_widget = pg.PlotWidget(background="white")
        self.plot_widget.setYRange(-1, 1)
        layout.addWidget(self.plot_widget)
        self.plot_widget.setBackground(
            QColor(255, 255, 255, 0)  # White with 0% opacity
        )
        self.plot_widget.getAxis("left").setVisible(False)
        self.plot_widget.getAxis("bottom").setVisible(False)
        self.plot_widget.setMenuEnabled(False)
        self.plot_widget.setMouseTracking(False)

        # Recording Timer Display
        self.recording_timer_label = create_label(
            "00:00:00", "font-size: 30px;", align="c"
        )
        layout.addWidget(self.recording_timer_label)

        # Media Control Buttons
        media_layout = QHBoxLayout()
        self.pause_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_MediaPause),
            func=self.__pause,
            stylesheet="modern",
            disable=True,
        )
        self.pause_button.setToolTip("Pause")
        self.play_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_MediaPlay),
            func=self.__play,
            stylesheet="modern",
            disable=True,
        )
        self.play_button.setToolTip("Play")
        self.stop_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_MediaStop),
            func=self.__stop,
            stylesheet="modern",
            disable=True,
        )
        self.rec_button = Create_Button(
            icon=QIcon(SVG_Icon["MIC"]),
            stylesheet="modern",
            func=self.__rec,
        )
        self.rec_button.setToolTip("Recording")
        self.save_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_DialogSaveButton),
            stylesheet="modern",
            func=self.save_audio,
            disable=True,
        )
        self.save_button.setToolTip("Save")
        media_layout.addWidget(self.pause_button)
        media_layout.addWidget(self.play_button)
        media_layout.addWidget(self.stop_button)
        media_layout.addWidget(self.rec_button)
        media_layout.addWidget(self.save_button)

        layout.addLayout(media_layout)

        # Progress Bar
        self.progress_bar = QProgressBar(self)
        self.progress_bar.setAlignment(Qt.AlignCenter)
        self.progress_bar.setRange(0, 100)  # Set range from 0 to 100
        self.progress_bar.setTextVisible(False)
        self.progress_bar.setStyleSheet(
            """
            QProgressBar {
                border: 2px solid #555;
                border-radius: 5px;
                height: 0.5em;
                background-color: #e0e0e0;
            }
            QProgressBar::chunk {
                background-color: #76c7c0;
                border-radius: 5px;
            }
        """
        )
        layout.addWidget(self.progress_bar)

        # Additional Features Layout
        feature_layout = QHBoxLayout()

        # Run Audacity Button
        self.audacity_button = Create_Button(
            "Run Audacity",
            lambda: Run_Audacity(self.recorder_service.__str__()),
            stylesheet="modern",
            disable=True,
        )
        self.audacity_button.setToolTip("Audacity Run")
        feature_layout.addWidget(self.audacity_button)

        # Accept Button
        self.accept_button = Create_Button(
            "Accept",
            stylesheet="modern",
            func=self.close,
            disable=True,
        )
        self.accept_button.setToolTip("Accept and Exit")
        feature_layout.addWidget(self.accept_button)
        layout.addLayout(feature_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        self.setup_shortcuts()
        self.curve = self.plot_widget.plot(pen="g")

    def setup_shortcuts(self):
        """Sets up keyboard shortcuts for the application."""
        # Shortcut for starting recording
        QShortcut(QKeySequence("r"), self, self.__rec)

        # Shortcut for stopping recording or playback
        QShortcut(QKeySequence("s"), self, self.__stop)

        # Shortcut for playing audio
        QShortcut(QKeySequence("p"), self, self.__play)

        # Shortcut for pausing audio
        QShortcut(QKeySequence("t"), self, self.__pause)

        # Shortcut for saving audio
        QShortcut(QKeySequence("Ctrl+s"), self, self.save_audio)

        # Shortcut for accepting and closing the application
        QShortcut(QKeySequence("Ctrl+q"), self, self.close)

    def populate_device_list(self):
        """Populates the device combo box with available audio devices."""
        self.device_combo.addItems(self.recorder_service.get_devices_name())

    def set_device_index(self, index):
        """
        Sets the currently selected device index and updates the status bar.

        Args:
            index: The index of the selected device.
        """
        self.status_bar.showMessage("Device: {}".format(index))
        self.device_index = self.device_combo.itemData(index)

    def start_timer(self):
        """Starts the timer for updating the waveform chart."""
        self.waveform_chart_timer.start(50)  # Update plot every 50 ms

    def stop_timer(self):
        """Stops the timer for updating the waveform chart."""
        self.waveform_chart_timer.stop()

    def reset_timer(self):
        """Resets the recording timer display."""
        self.stop_timer()  # Stop the timer if it's running
        self.recording_timer_label.reset()  # Reset display

    def update_plot(self):
        """Updates the waveform plot with the latest audio data."""
        if self.recorder_service.frames:
            # Convert the last chunk of frames to numpy array
            data = np.frombuffer(self.recorder_service.frames[-1], dtype=np.int16)
            data = data / 32768.0  # Normalize to [-1, 1]

            # time = np.linspace(
            #     self.recorder_service.get_recording_duration() - 1,
            #     self.recorder_service.get_recording_duration(),
            #     num=len(data),
            # )

            self.curve.setData(data)

            self.recording_timer_label.setText(
                self.recorder_service.get_recording_format_duration()
            )

    def update_progress_bar(self):
        """Updates the progress bar based on the current playback status."""
        if self.recorder_service.is_playing:
            # current_duration = (
            #     self.recorder_service.get_recording_duration()
            # )  # Total duration in seconds
            total_frames = len(self.recorder_service.frames)  # Total frames recorded
            if total_frames > 0:
                current_frame = (
                    self.recorder_service.current_playback_frame_index
                )  # This should be updated during playback
                progress = (
                    current_frame / total_frames
                ) * 100  # Calculate progress percentage
                self.progress_bar.setValue(progress)  # Update the progress bar

                if current_frame >= total_frames:
                    self.__stop()  # Automatically stop playback if the end is reached
                    self.progress_bar.setValue(100)  # Set progress bar to 100%
        else:
            self.progress_timer.stop()  # Stop the timer if not playing
            self.__stop()

    def __pause(self):
        """Pauses the audio recording if currently recording."""
        if self.recorder_service.is_recording:
            self.recorder_service.pause_recording()

    def __play(self):
        """Starts playback of the recorded audio."""
        if (
            not self.recorder_service.is_playing
            and not self.recorder_service.is_recording
        ):
            self.recorder_service.play_playback()
            self.play_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.pause_button.setDisabled(False)
            self.rec_button.setDisabled(True)
            # Start the progress bar timer
            self.progress_timer.start(100)  # Update every 100 ms
            self.progress_bar.setValue(0)

    def __stop(self):
        """Stops the audio recording or playback."""
        if self.recorder_service.is_recording:
            self.status_bar.showMessage("Status: Re-recording")
            self.recorder_service.stop_recording()
            self.stop_timer()
        elif self.recorder_service.is_playing:
            self.recorder_service.stop_playback()
        self.stop_button.setDisabled(True)
        self.pause_button.setDisabled(True)
        self.play_button.setDisabled(False)
        self.rec_button.setDisabled(False)
        self.save_button.setDisabled(False)
        self.accept_button.setDisabled(False)

    def __rec(self):
        """Starts audio recording."""
        if not self.recorder_service.is_recording:
            self.status_bar.showMessage("Status : Recording ...")
            self.rec_button.setDisabled(True)
            self.play_button.setDisabled(True)
            self.save_button.setDisabled(True)
            self.pause_button.setDisabled(False)
            self.stop_button.setDisabled(False)

            self.recorder_service.set_device_index(self.device_index)
            self.recorder_service.set_channels(self.device_index)
            self.recorder_service.start_recording()
            self.recording_timer_label.reset()
            self.start_timer()

    def get_audio_basename(self) -> str:
        """
        Generates a unique audio file name based on the current date and time.

        Returns:
            str: The generated audio file name.
        """
        now = datetime.datetime.now()
        return "Voice_{}".format(now.strftime("%d%m%Y_%H%M%S"))

    def save_audio(self):
        """Saves the recorded audio to a file."""
        if self.recorder_service.is_recording:
            self.recorder_service.stop_recording()
        if self.recorder_service.is_playing:
            self.recorder_service.stop_playback()
        if self.recorder_service.frames:
            self.recorder_service.save_recording()
            self.File_Saved = True
            self.audacity_button.setDisabled(False)
        else:
            show_message("No Recording", "Please record before saving the file.")

    def closeEvent(self, event):
        """Handles the close event of the main window."""
        if not self.File_Saved:
            if (
                show_message("Confirmation", "Do you want to save the audio file?")
                == QMessageBox.Yes
            ):
                self.save_audio()
        event.accept()  # Accept the event to close the window

    def resetUI(self):
        """Resets the user interface to its initial state."""
        self.File_Saved = False
        self.message_label.reset()  # Clear message label
        self.recording_timer_label.reset()  # Reset timer display
        self.progress_bar.setValue(0)  # Reset progress bar
        self.status_bar.clearMessage()  # Clear status bar message

        # Enable/disable buttons to their original state
        self.pause_button.setDisabled(True)
        self.play_button.setDisabled(False)
        self.stop_button.setDisabled(True)
        self.rec_button.setDisabled(False)
        self.save_button.setDisabled(True)
        self.accept_button.setDisabled(True)
        self.audacity_button.setDisabled(True)
        self.message_object.reset()
        # Clear the waveform plot
        self.curve.setData([])  # Clear the plot data

    def record(
        self,
        path: str = None,
        msg: str = None,
        voice_id: int = None,
        svg_path: any = None,
        show: bool = True,
        **kwargs,
    ):
        """
        Prepares the recorder for a new recording session.

        Args:
            path (str): The file path to save the recording.
            msg (str): The message to display in the UI.
            voice_id (int): An identifier for the voice.
            svg_path: The path to the SVG file to display.
            **kwargs: Additional keyword arguments.
        """
        self.resetUI()
        if path is not None:
            self.recorder_service.set_filepath(path)
        if svg_path is not None:
            svg_path = str(svg_path)
            # self.message_object.setStyleSheet("background-color: white; padding: 20px;")
            self.message_object.load_svg(svg_path)
            # self.setSvg_Size(svg_path)

        if msg is not None:
            self.message_label.setText(msg)
        if voice_id is not None:
            self.setWindowTitle("Sound ID : {}".format(voice_id))
            # self.speech_script_label.setText("Sound ID : {}".format(voice_id))
        if show:
            self.show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    audiorecoder = PyAudio_()
    recorder = Recorder(audiorecoder)
    recorder.record(path=recorder.get_audio_basename() + ".wav", msg="Start Recording")
    recorder.show()
    sys.exit(app.exec())
