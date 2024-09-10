import os
from typing import overload
import xml.etree.ElementTree as ET
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
)
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QSize, QRectF
from PySide6.QtSvgWidgets import QSvgWidget
from PySide6.QtSvg import QSvgRenderer


def PWD():
    """Returns the directory of the current file."""
    return os.path.dirname(__file__)


def is_dark_mode():
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
        """Sets the properties of the label."""
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
                "; ".join(style).strip() + ";"  # Ensure styles are properly formatted
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


def WindowCenter(parent, onTop=False):
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


def show_message(title, message, icon=QMessageBox.Information, parent=None):
    """
    Displays a message box with the specified title and message.

    Args:
        title: The title of the message box.
        message: The message to display.

    Returns:
        int: The button clicked by the user.
    """
    msg_box = QMessageBox(parent)
    msg_box.setWindowTitle(title)
    msg_box.setText(message)
    msg_box.setIcon(QMessageBox.Information)
    msg_box.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
    return msg_box.exec()  # Show the message box


class SVG_Viewer(QSvgWidget):
    """Custom QSvgWidget class for displaying and interacting with SVG files."""

    def __init__(self, svg_file: str = None, padding: int = 10, parent=None):
        """Initializes the SVG_Viewer with an optional SVG file and padding.

        Args:
            svg_file (str, optional): Path to the SVG file to load.
            padding (int, optional): Padding around the SVG content.
            parent: The parent widget for the SVG viewer.
        """
        super().__init__(parent)
        self.original_size = None  # Store the original size
        self.scale_factor = 1.0  # Initial scale factor
        self.padding = padding  # Padding around the SVG content
        if svg_file:
            self.original_svg = svg_file
        else:
            self.original_svg = SVG_Icon["MIC"]  # Default icon if no file is provided
        self.load_svg(self.original_svg)

    def load_svg(self, svg_file):
        """Loads the specified SVG file into the viewer.

        Args:
            svg_file (str): Path to the SVG file to load.
        """
        if svg_file:
            self.renderer = QSvgRenderer(svg_file)
            if not self.renderer.isValid():
                print("Invalid SVG file.")
                return
            self.load(svg_file)
            self.original_size = self.renderer.defaultSize()
            self.setFixedSize(self.original_size * self.scale_factor)
            self.update()  # Update the widget to reflect changes

    def reset(self):
        """Resets the SVG viewer to its original state."""
        if self.original_size:
            self.load_svg(self.original_svg)
            self.scale_factor = 1.0  # Reset scale factor
            self.setFixedSize(self.original_size)  # Reset to original size
            self.update()  # Update the widget to reflect changes

    def wheelEvent(self, event: QWheelEvent):
        """Handles mouse wheel events for zooming in and out of the SVG.

        Args:
            event (QWheelEvent): The wheel event containing the scroll direction.
        """
        if event.angleDelta().y() > 0:
            self.scale_factor *= 1.1  # Zoom in
        else:
            self.scale_factor /= 1.1  # Zoom out

        # Apply the scaling
        self.setFixedSize(self.original_size * self.scale_factor)
        self.update()  # Update the widget to reflect changes

    def resizeEvent(self, event):
        """Handles resize events to adjust the SVG view accordingly.

        Args:
            event: The resize event.
        """
        super().resizeEvent(event)
        self.setFixedSize(self.original_size * self.scale_factor)

    def paintEvent(self, event):
        """Handles paint events to customize the rendering of the SVG.

        Args:
            event: The paint event.
        """
        painter = QPainter(self)
        painter.fillRect(self.rect(), QColor(255, 255, 255))  # White background

        # Adjust the drawing area for padding
        svg_rect = self.rect().adjusted(
            self.padding, self.padding, -self.padding, -self.padding
        )
        painter.setClipRect(svg_rect)  # Set the clipping rectangle for the SVG

        super().paintEvent(event)  # Call the base class implementation


def setup_shortcuts(parent, keys):
    """Sets up keyboard shortcuts for the application."""
    for key in keys:
        QShortcut(QKeySequence(key), parent, keys[key])
