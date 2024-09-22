"""
This module provides a set of custom widgets and utility functions for a PySide6 application.
It includes:

1. **create_label**: A custom QLabel with additional styling and alignment options.
2. **Create_Button**: A custom QPushButton with enhanced functionality and styling.
3. **ImageDisplay**: A widget for displaying images with zoom functionality and a message box.
4. **Audio_Waveform**: A widget for displaying audio waveforms using pyqtgraph.
5. **Audio_Playback_Progress_bar**: A custom progress bar for audio playback.

Utility functions include:
- `PWD()`: Returns the directory of the current file.
- `is_dark_mode()`: Checks if the application is in dark mode.
- `WindowCenter()`: Centers a given window on the screen.
- `show_message()`: Displays a message box with a title and message.
- `setup_shortcuts()`: Sets up keyboard shortcuts for the application.
"""

import sys
import os
from typing import overload
import xml.etree.ElementTree as ET
from PIL import Image, ImageQt
from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap, QImage
from PySide6.QtGui import (
    QIcon,
    QPalette,
    QPainter,
    QColor,
    QFont,
    QWheelEvent,
    QTransform,
    QShortcut,
    QKeySequence,
)
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
    QTextEdit,
    QScrollArea,
    QSizePolicy,
    QProgressBar,
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QRectF
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer
import pyqtgraph as pg


def PWD() -> str:
    """Returns the directory of the current file."""
    return os.path.dirname(__file__)


def is_dark_mode() -> bool:
    """Determines if the application is in dark mode based on the window background color.

    Returns:
        bool: True if dark mode is enabled, False otherwise.
    """
    palette = QApplication.palette()
    window_color = palette.window().color()
    return window_color.lightness() < 128  # Dark mode if lightness is less than 128


# Load SVG icons based on the current mode (dark or light)
SVG_Icon = {}
if is_dark_mode():
    SVG_Icon = {
        "PLAY": os.path.join(PWD(), "assets/dark_mode/play.svg"),
        "STOP": os.path.join(PWD(), "assets/dark_mode/stop.svg"),
        "PAUSE": os.path.join(PWD(), "assets/dark_mode/pause.svg"),
        "MIC": os.path.join(PWD(), "assets/dark_mode/mic.svg"),
    }
else:
    SVG_Icon = {
        "PLAY": os.path.join(PWD(), "assets/light_mode/play.svg"),
        "STOP": os.path.join(PWD(), "assets/light_mode/stop.svg"),
        "PAUSE": os.path.join(PWD(), "assets/light_mode/pause.svg"),
        "MIC": os.path.join(PWD(), "assets/light_mode/mic.svg"),
    }


class create_label(QLabel):
    """Custom QLabel class with additional properties for styling and alignment."""

    def __init__(
        self,
        text: str,
        *style: str,
        align: str | Qt.AlignmentFlag = None,
        wordwrap: bool = False,
        parent=None,
        **kwargs,
    ):
        """Initializes a create_label with customizable properties.

        Args:
            text (str): The text to display on the label.
            *style (str): CSS style strings to apply to the label.
            align (str | Qt.AlignmentFlag, optional): Alignment of the text.
                Can be 'c' for center, 'l' for left, or a Qt.AlignmentFlag.
            wordwrap (bool, optional): Whether to enable word wrapping.
            parent: The parent widget for the label.
            **kwargs: Additional keyword arguments for QLabel.
        """
        super(create_label, self).__init__(text, parent, **kwargs)

        # Store original properties
        self.original_text = text
        self.original_style = "; ".join(style).strip() + ";" if style else ""
        self.original_alignment = align
        self.original_wordwrap = wordwrap

        # Set initial properties
        self.set_properties(text, style, align, wordwrap)

    def set_properties(
        self, text: str, style: tuple, align: str | Qt.AlignmentFlag, wordwrap: bool
    ):
        """Sets the properties of the label.

        Args:
            text (str): The text to display on the label.
            style (tuple): CSS style strings to apply to the label.
            align (str | Qt.AlignmentFlag): Alignment of the text.
            wordwrap (bool): Whether to enable word wrapping.
        """
        self.setText(text)

        # Set alignment based on the provided argument
        if align in (Qt.AlignmentFlag.AlignCenter, "c"):
            self.setAlignment(Qt.AlignCenter)
        elif align in (Qt.AlignmentFlag.AlignLeft, "l"):
            self.setAlignment(Qt.AlignLeft)
        elif align in (Qt.AlignmentFlag.AlignRight, "r"):
            self.setAlignment(Qt.AlignRight)

        # Enable word wrapping if specified
        self.setWordWrap(wordwrap)

        # Apply styles if provided
        if style:
            style_str = (
                # Ensure styles are properly formatted
                "; ".join(style).strip()
                + ";"
            )
            self.setStyleSheet(style_str)

    def reset(self):
        """Resets the label to its original state."""
        self.set_properties(
            self.original_text,
            self.original_style.split("; ") if self.original_style else [],
            self.original_alignment,
            self.original_wordwrap,
        )


class Create_Button(QPushButton):
    """Custom QPushButton class with additional properties for functionality and styling."""

    def __init__(
        self,
        text: str = None,
        func: callable = None,
        icon: QIcon = None,
        shortcut: str = None,
        stylesheet: str = "",
        disable=False,
        toolTip=None,
        **kwargs,
    ):
        """Initializes a Create_Button with customizable properties.

        Args:
            text (str, optional): The text to display on the button.
            func (callable, optional): Function to connect to the button's click event.
            icon (QIcon, optional): Icon to display on the button.
            shortcut (str, optional): Keyboard shortcut for the button.
            stylesheet (str, optional): Custom stylesheet for the button.
            disable (bool, optional): Whether to disable the button initially.
            toolTip (str, optional): Tooltip text for the button.
            **kwargs: Additional keyword arguments for QPushButton.
        """
        super().__init__(text, **kwargs)

        # Store original state
        self.original_text = text
        self.original_icon = icon
        self.original_disabled = disable

        # Set the button properties
        if text is not None:
            self.setText(text)

        if func is not None:
            self.clicked.connect(func)

        if icon:
            self.setIcon(icon)

        if shortcut:
            self.setShortcut(shortcut)

        if toolTip:
            self.setToolTip(toolTip)

        # Set the stylesheet
        self.setStyle(stylesheet)

        # Set the disabled state
        self.setDisabled(disable)

    def setStyle(self, stylesheet: str):
        """Sets the style of the button based on the provided stylesheet.

        Args:
            stylesheet (str): The stylesheet to apply to the button.
        """
        match stylesheet:
            case "modern":
                self.setStyleSheet(
                    """
                    QPushButton {
                        background-color: #4CAF50; /* Green */
                        color: white;
                        border: none;
                        padding: 15px 15px;
                        text-align: center;
                        text-decoration: none;
                        font-size: 16px;
                        margin: 4px 2px;
                        border-radius: 12px; /* Rounded corners */
                    }
                    QPushButton:hover {
                        background-color: #45a049; /* Darker green on hover */
                    }
                    QPushButton:pressed {
                        background-color: #3e8e41; /* Even darker green when pressed */
                    }
                    QPushButton:disabled {
                        background-color: #cccccc; /* Gray background when disabled */
                        color: #666666; /* Gray text when disabled */
                    }
                    """
                )
            case str():
                self.setStyleSheet(stylesheet)

    def reset(self):
        """Reset the button to its original state."""
        if self.original_text:
            self.setText(self.original_text)
        if self.original_icon:
            self.setIcon(self.original_icon)
        self.setDisabled(self.original_disabled)


def WindowCenter(parent: QWidget, onTop: bool = False) -> None:
    """Centers the given window on the screen.

    Args:
        parent: The window to center.
        onTop (bool, optional): If True, sets the window to stay on top of others.
    """
    screen_geometry = parent.screen().availableGeometry()
    window_geometry = parent.geometry()

    # Calculate the center position
    x = (screen_geometry.width() - window_geometry.width()) // 2
    y = (screen_geometry.height() - window_geometry.height()) // 2

    # Move the window to the center
    parent.move(x, y)

    if onTop:
        parent.setWindowFlag(parent.windowFlags() | Qt.WindowStaysOnTopHint)


def show_message(title: str, message: str, icon=QMessageBox.Information, parent=None) -> int:
    """Displays a message box with the specified title and message.

    Args:
        title (str): The title of the message box.
        message (str): The message to display.
        icon (QMessageBox.Icon, optional): The icon to display in the message box.
        parent (QWidget, optional): The parent widget for the message box.

    Returns:
        int: The button clicked by the user.
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(icon)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg_box.exec()  # Show the message box


def setup_shortcuts(parent: QWidget, keys: dict) -> None:
    """Sets up keyboard shortcuts for the application.

    Args:
        parent (QWidget): The parent widget to which the shortcuts are applied.
        keys (dict): A dictionary mapping key sequences to functions.
    """
    for key in keys:
        QShortcut(QKeySequence(key), parent, keys[key])


class ImageDisplay(QWidget):
    """Widget for displaying images with zoom functionality and a message box."""

    def __init__(self, parent=None):
        """Initializes the ImageDisplay widget.

        Args:
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent=parent)
        self.main_parent = parent
        # Create a vertical layout
        self.layout = QVBoxLayout(self)
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setFixedSize(parent.size())
        # Create QLabel for image display
        self.image_label = QLabel()
        self.scroll_area.setWidget(self.image_label)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.scroll_area)

        # Create QTextEdit for text input
        self.message_box = QTextEdit()
        self.message_box.setText("Message")
        self.message_box.setStyleSheet("color:orange; font-size: 15px;")

        self.layout.addWidget(self.message_box)

        self.scale_factor = 1.0  # To keep track of the zoom level
        self.load_image(None)

    def pil_to_qimage(self, pil_image: Image.Image) -> QImage:
        """Convert a Pillow image to a QImage.

        Args:
            pil_image (Image.Image): The Pillow image to convert.

        Returns:
            QImage: The converted QImage.
        """
        if pil_image.mode != "RGBA":
            pil_image = pil_image.convert("RGBA")
        data = pil_image.tobytes("raw", "RGBA")
        qimage = QImage(data, pil_image.width, pil_image.height, QImage.Format_RGBA8888)
        return qimage

    def load_image(
        self,
        file_name,
        label_text: str = "Failed to load image.",
        msg: str = None,
    ) -> None:
        """Loads an image from a file or a PIL image and displays it.

        Args:
            file_name (str | Image.Image): The path to the image file or a PIL image.
            label_text (str, optional): Text to display if loading fails.
            msg (str, optional): Message to set in the message box.
        """
        pixmap = QPixmap()
        if isinstance(file_name, Image.Image):
            file_name = self.pil_to_qimage(file_name)
            pixmap = QPixmap.fromImage(file_name)
        elif isinstance(file_name, str):
            if os.path.exists(file_name):
                pixmap = QPixmap(file_name)
            else:
                label_text = f"{file_name} is not found!"
        elif file_name is None:
            label_text = "Say"

        self.set_message_box(msg)

        if pixmap.isNull():
            self.image_label.setText(label_text)
        else:
            self.original_pixmap = pixmap  # Store the original pixmap for scaling
            self.image_label.setPixmap(
                pixmap.scaled(
                    pixmap.size() / 2,
                )
            )
            self.image_label.setText("")  # Clear the text when an image is loaded

    def zoom_in(self) -> None:
        """Zooms in on the displayed image."""
        self.scale_factor *= 1.2  # Increase the scale factor
        self.update_image()

    def zoom_out(self) -> None:
        """Zooms out of the displayed image."""
        self.scale_factor /= 1.2  # Decrease the scale factor
        self.update_image()

    def update_image(self) -> None:
        """Updates the displayed image based on the current zoom level."""
        if hasattr(self, "original_pixmap"):
            scaled_pixmap = self.original_pixmap.scaled(
                self.original_pixmap.size() * self.scale_factor,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.image_label.setPixmap(scaled_pixmap)

    def wheelEvent(self, event: QWheelEvent) -> None:
        """Handles the wheel event for zooming in and out.

        Args:
            event (QWheelEvent): The wheel event.
        """
        # Zoom in or out based on the scroll direction
        if event.angleDelta().y() > 0:
            self.zoom_in()
        else:
            self.zoom_out()
        event.ignore()

    def set_message_box(self, text: str | None) -> None:
        """Set the text in the QTextEdit. Pass None to clear it.

        Args:
            text (str | None): The text to set in the message box or None to clear it.
        """
        
        if text is None:
            self.message_box.clear()  # Clear the text edit
        elif isinstance(text, str):
            self.message_box.setText(text)  # Set the text to the provided string
        else:
            print("Invalid input: text must be a string or None.")


class Audio_Waveform(pg.PlotWidget):
    """Widget for displaying audio waveforms."""

    def __init__(self, parent=None):
        """Initializes the Audio_Waveform widget.

        Args:
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent=parent, background="white")
        self.setYRange(-1, 1)
        self.setBackground(QColor(255, 255, 255, 0))  # White with 0% opacity
        self.getAxis("left").setVisible(False)
        self.getAxis("bottom").setVisible(False)
        self.setMenuEnabled(False)
        self.setMouseTracking(False)


class Audio_Playback_Progress_bar(QProgressBar):
    """Custom progress bar for audio playback."""

    def __init__(self, parent=None):
        """Initializes the Audio_Playback_Progress_bar.

        Args:
            parent (QWidget, optional): The parent widget.
        """
        super().__init__(parent=parent)
        self.setAlignment(Qt.AlignCenter)
        self.setRange(0, 100)
        self.setTextVisible(False)
        self.setStyleSheet(
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



