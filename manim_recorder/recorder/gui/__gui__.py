"""
This module provides a GUI application for recording audio using PySide6.
It includes features for recording, playing back, and saving audio files.

Classes:
1. **Recorder**: The main class for the audio recorder application, handling UI and audio recording functionalities.

Methods:
- `__init__`: Initializes the Recorder application.
- `initUI`: Sets up the user interface components.
- `populate_device_list`: Populates the device combo box with available audio devices.
- `set_device_index`: Sets the currently selected device index and updates the status bar.
- `start_timer`: Starts the timer for updating the waveform chart.
- `stop_timer`: Stops the timer for updating the waveform chart.
- `reset_timer`: Resets the recording timer display.
- `update_plot`: Updates the waveform plot with the latest audio data.
- `update_progress_bar`: Updates the progress bar based on the current playback status.
- `__pause`: Pauses the audio recording or playback.
- `__play`: Starts playback of the recorded audio.
- `__stop`: Stops the audio recording or playback.
- `__rec`: Starts audio recording.
- `_next`: Handles the action for the 'Next' button.
- `_save`: Saves the recorded audio to a file.
- `resetUI`: Resets the user interface to its initial state.
- `_recorder`: Handles the recorder data received from the communicator.
"""

import sys
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QLabel,
    QVBoxLayout,
    QPushButton,
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
from manim_recorder.recorder.gui.config import (
    create_label,
    Create_Button,
    WindowCenter,
    ImageDisplay,
    SVG_Icon,
    show_message,
    setup_shortcuts,
    Audio_Waveform,
    Audio_Playback_Progress_bar,
)
from manim_recorder.helper import get_audio_basename, logger


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
        communicator=None,
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
        self.communicator = communicator
        if self.communicator:
            self.communicator.recorder_data.connect(self._recorder)

    def initUI(self) -> None:
        """Initializes the user interface components."""
        self.setWindowTitle("Audio Recorder")
        self.setGeometry(100, 100, 600, 400)
        WindowCenter(self, onTop=True)

        layout = QVBoxLayout()

        # Device Index List
        self.device_combo = QComboBox()
        self.device_combo.currentIndexChanged.connect(self.set_device_index)
        layout.addWidget(self.device_combo)

        # Image Display and Text Editor
        self.message_object = ImageDisplay(self)
        layout.addWidget(self.message_object)

        # Waveform Chart
        self.plot_widget = Audio_Waveform(self)
        layout.addWidget(self.plot_widget)

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
            toolTip="Pause (<b>t</b>)",
        )
        self.play_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_MediaPlay),
            func=self.__play,
            stylesheet="modern",
            disable=True,
            toolTip="Play (<b>p</b>)",
        )
        self.stop_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_MediaStop),
            func=self.__stop,
            stylesheet="modern",
            disable=True,
            toolTip="Stop (<b>s</b>)",
        )
        self.rec_button = Create_Button(
            icon=QIcon(SVG_Icon["MIC"]),
            stylesheet="modern",
            func=self.__rec,
            toolTip="Recording (<b>r</b>)",
        )

        self.save_button = Create_Button(
            icon=self.style().standardIcon(QStyle.SP_DialogSaveButton),
            stylesheet="modern",
            func=self._save,
            disable=True,
            toolTip="Save (<b>Ctrl + S</b>)",
        )

        media_layout.addWidget(self.pause_button)
        media_layout.addWidget(self.play_button)
        media_layout.addWidget(self.stop_button)
        media_layout.addWidget(self.rec_button)
        media_layout.addWidget(self.save_button)

        layout.addLayout(media_layout)

        # Progress Bar
        self.progress_bar = Audio_Playback_Progress_bar(self)
        layout.addWidget(self.progress_bar)

        # Additional Features Layout
        feature_layout = QHBoxLayout()

        # Run Audacity Button
        self.audacity_button = Create_Button(
            "Run Audacity",
            lambda: Run_Audacity(self.recorder_service.__str__()),
            stylesheet="modern",
            disable=True,
            toolTip="Audacity Run",
        )
        feature_layout.addWidget(self.audacity_button)

        # Accept Button
        self.accept_button = Create_Button(
            "Next",
            stylesheet="modern",
            func=self._next,
            disable=True,
            toolTip="Accept and Next (<b>a</b>)",
        )

        feature_layout.addWidget(self.accept_button)
        layout.addLayout(feature_layout)

        # Status Bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Loading ...")

        container = QWidget()
        container.setLayout(layout)
        self.setCentralWidget(container)
        setup_shortcuts(
            self,
            {
                "r": self.__rec,
                "s": self.__stop,
                "p": self.__play,
                "t": self.__pause,
                "Ctrl+S": self._save,
                "a": self._next,
                "Ctrl+Q": self.close,
            },
        )
        self.curve = self.plot_widget.plot(pen="g")

    def populate_device_list(self) -> None:
        """Populates the device combo box with available audio devices."""
        self.device_combo.addItems(self.recorder_service.get_devices_name())

    def set_device_index(self, index: int) -> None:
        """
        Sets the currently selected device index and updates the status bar.

        Args:
            index (int): The index of the selected device.
        """
        self.status_bar.showMessage("Device: {}".format(index))
        self.device_index = self.device_combo.itemData(index)

    def start_timer(self) -> None:
        """Starts the timer for updating the waveform chart."""
        self.waveform_chart_timer.start(50)  # Update plot every 50 ms

    def stop_timer(self) -> None:
        """Stops the timer for updating the waveform chart."""
        self.waveform_chart_timer.stop()

    def reset_timer(self) -> None:
        """Resets the recording timer display."""
        self.stop_timer()  # Stop the timer if it's running
        self.recording_timer_label.reset()  # Reset display

    def update_plot(self) -> None:
        """Updates the waveform plot with the latest audio data."""
        if self.recorder_service:
            # Convert the last chunk of frames to numpy array
            data = None

            if self.recorder_service.is_recording:
                data = np.frombuffer(self.recorder_service[-1], dtype=np.int16)
                self.recording_timer_label.setText(
                    self.recorder_service.get_recording_format_duration()
                )
            elif (
                self.recorder_service.is_playing
                and self.recorder_service.current_playback_frame_index
                < len(self.recorder_service)
            ):
                data = np.frombuffer(
                    self.recorder_service[
                        self.recorder_service.current_playback_frame_index
                    ],
                    dtype=np.int16,
                )

            if all(data if data is not None else [False]):
                data = data / 32768.0  # Normalize to [-1, 1]

                self.curve.setData(data)

    def update_progress_bar(self) -> None:
        """Updates the progress bar based on the current playback status."""
        if self.recorder_service.is_playing:
            total_frames = len(self.recorder_service)  # Total frames recorded
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

    def __pause(self) -> None:
        """Pauses the audio recording if currently recording."""
        if self.recorder_service.is_recording:
            if not self.recorder_service.is_paused:
                self.recorder_service.pause_recording()
            else:
                self.recorder_service.resume_recording()
        elif self.recorder_service.is_playing:
            if not self.recorder_service.playback_paused:
                self.recorder_service.pause_playback()
            else:
                self.recorder_service.resume_playback()

    def __play(self) -> None:
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
            self.start_timer()

    def __stop(self) -> None:
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
        self.audacity_button.setDisabled(True)
        self.accept_button.setDisabled(False)

    def __rec(self) -> None:
        """Starts audio recording."""
        if not self.recorder_service.is_recording:
            self.status_bar.showMessage("Status : Recording ...")

            self.pause_button.setDisabled(False)
            self.play_button.setDisabled(True)
            self.stop_button.setDisabled(False)
            self.rec_button.setDisabled(True)
            self.save_button.setDisabled(True)
            self.audacity_button.setDisabled(True)
            self.accept_button.setDisabled(True)
            self.recorder_service.set_device_index(self.device_index)
            self.recorder_service.set_channels(self.device_index)
            self.recorder_service.start_recording()
            self.recording_timer_label.reset()
            self.start_timer()

    def _next(self) -> None:
        """Handles the action for the 'Next' button."""
        if not self.File_Saved:
            if (
                show_message("Confirmation", "Do you want to save the audio file?")
                == QMessageBox.Yes
            ):
                self._save()
        self.pause_button.setDisabled(True)
        self.play_button.setDisabled(True)
        self.stop_button.setDisabled(True)
        self.rec_button.setDisabled(True)
        self.save_button.setDisabled(True)
        self.accept_button.setDisabled(True)
        self.audacity_button.setDisabled(True)
        logger.info("Audio File : {}".format(self.recorder_service.__str__()))
        self.status_bar.showMessage("Loading ...")
        if self.communicator:
            self.communicator.accept.emit(self.recorder_service.__str__())

    def _save(self) -> None:
        """Saves the recorded audio to a file."""
        if self.recorder_service.is_recording:
            self.recorder_service.stop_recording()
        if self.recorder_service.is_playing:
            self.recorder_service.stop_playback()
        if self.recorder_service:
            self.recorder_service.save_recording()
            self.File_Saved = True
            self.audacity_button.setDisabled(False)
        else:
            show_message("No Recording", "Please record before saving the file.")

    def resetUI(self) -> None:
        """Resets the user interface to its initial state."""
        self.File_Saved = False
        self.recording_timer_label.reset()  # Reset timer display
        self.progress_bar.setValue(0)  # Reset progress bar
        self.status_bar.clearMessage()  # Clear status bar message
        self.recorder_service.frames = []
        # Enable/disable buttons to their original state
        self.pause_button.setDisabled(True)
        self.play_button.setDisabled(True)
        self.stop_button.setDisabled(True)
        self.rec_button.setDisabled(False)
        self.save_button.setDisabled(True)
        self.accept_button.setDisabled(True)
        self.audacity_button.setDisabled(True)
        # Clear the waveform plot
        self.curve.setData([])  # Clear the plot data

    def _recorder(
        self,
        path: str = None,
        msg: str = None,
        voice_id: int = None,
        mobject: str = None,
    ) -> None:
        """Handles the recorder data received from the communicator.

        Args:
            path (str, optional): The file path for the audio.
            msg (str, optional): A message to display.
            voice_id (int, optional): The ID of the voice.
            mobject (str, optional): The mobject to display.
        """
        self.resetUI()
        if path is not None:
            self.recorder_service.set_filepath(path)

        self.message_object.load_image(mobject, msg=msg)
        if voice_id is not None:
            self.setWindowTitle("Sound ID : {}".format(voice_id))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    audiorecoder = PyAudio_()
    recorder = Recorder(audiorecoder)
    recorder.show()
    sys.exit(app.exec())
