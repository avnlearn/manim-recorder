"""
Helper for manim-recorder
"""

import json
import os
import textwrap
import datetime
import platform  # Added import for platform
import logging
from manim import logger, Mobject


def Check_os():
    """
    Check the operating system and return its name.

    Returns:
        str: The name of the operating system (e.g., "Linux", "macOS", "Windows", "Termux (Android)", or "Unknown OS").
    """
    os_name = platform.system()
    match os_name:
        case "Linux":
            # Check for Termux by looking for the presence of the 'termux' directory
            if os.path.exists("/data/data/com.termux"):
                return "Termux (Android)"
            else:
                return "Linux"
        case "Darwin":
            return "macOS"
        case "Windows":
            return "Windows"
        case _:
            return "Unknown OS"


def get_audio_basename() -> str:
    """
    Generates a unique audio file name based on the current date and time.

    Returns:
        str: The generated audio file name.
    """
    now = datetime.datetime.now()
    return "Voice_{}".format(now.strftime("%d%m%Y_%H%M%S"))


def mobject_to_text(mobject: Mobject) -> str():
    # Tex() or MathTex()
    if hasattr(mobject, "get_tex_string"):
        mobject = mobject.get_tex_string()
    # Text
    elif hasattr(mobject, "original_text"):
        mobject = mobject.original_text
    # Paragraph
    elif hasattr(mobject, "lines_text"):
        mobject = mobject.lines_text.original_text
    else:
        mobject = str(mobject)
    return mobject


def text_and_mobject(text: str, mobject: Mobject, **kwargs) -> tuple():
    match [text, mobject]:
        case [None, Mobject()]:
            text = mobject_to_text(mobject)
            mobject = (
                mobject.get_file_path() if hasattr(mobject, "get_file_path") else None
            )
        case [str(), Mobject()]:
            try:
                mobject = (
                    mobject.get_file_path()
                    if hasattr(mobject, "get_file_path")
                    else None
                )
                
            except AttributeError as e:
                logging.error("mobject : {}".format(e))
                mobject = None
        case [None, str()]:
            text = mobject
            mobject = mobject if os.path.exists(mobject) else None
        case [Mobject(), None] | [Mobject(), str()] | [str(), None]:
            return text_and_mobject(mobject, text)
        case _:
            return None
    
    return text, mobject


def msg_box(msg, indent=1, width=None, title=None):
    """
    Create a message box with optional title and indentation.

    Args:
        msg (str): The message to display in the box.
        indent (int): The number of spaces to indent the message (default is 1).
        width (int, optional): The width of the message box. If None, it will be determined based on the message length.
        title (str, optional): The title of the message box.

    Returns:
        str: A formatted string representing the message box.
    """
    # Wrap lines that are longer than 80 characters
    if width is None and len(msg) > 80:
        width = 80
        lines = []
        for line in msg.splitlines():
            if len(line) > width:
                line = line[:width] + " " + line[width:]
            lines.extend(textwrap.wrap(line, width))
        msg = "\n".join(lines)

    lines = msg.split("\n")
    space = " " * indent
    if not width:
        width = max(map(len, lines))
    box = f'╔{"═" * (width + indent * 2)}╗\n'  # upper_border
    if title:
        box += f"║{space}{title:<{width}}{space}║\n"  # title
        box += f'║{space}{"-" * len(title):<{width}}{space}║\n'  # underscore
    box += "".join([f"║{space}{line:<{width}}{space}║\n" for line in lines])
    box += f'╚{"═" * (width + indent * 2)}╝'  # lower_border
    return box


def append_to_json_file(json_file: str, data: dict, voice_id: int = -1, **kwargs):
    """
    Append data to a JSON file. If the file does not exist, it will be created.

    Args:
        json_file (str): The path to the JSON file.
        data (dict): The data to append to the JSON file.
        voice_id (int, optional): The index of the voice data to update (default is -1, which appends).
        **kwargs: Additional keyword arguments (not used in this function).

    Raises:
        ValueError: If the JSON file does not contain a list.
    """
    # This cache.json file is not exist and Create cache.json file and append
    if not os.path.exists(json_file):
        with open(json_file, "w") as f:
            json.dump([data], f, indent=2)
        return

    # This cache.json file is exist and load
    with open(json_file, "r") as f:
        json_data = json.load(f)

    # Check cache.json file is list
    if not isinstance(json_data, list):
        raise ValueError("JSON file should be a list")

    if voice_id > -1 and 0 <= voice_id < len(json_data):
        cache_json_data = json_data[voice_id]
        if isinstance(cache_json_data, dict):
            if data.get("input_data") == cache_json_data.get("input_data"):
                return
            elif isinstance(cache_json_data.get("original_audio"), str):
                final_audio = cache_json_data.get("original_audio")
                final_audio = "{}/{}".format(os.path.dirname(json_file), final_audio)
                if os.path.exists(final_audio):
                    os.remove(final_audio)

        json_data[voice_id] = data
        return
    else:
        json_data.append(data)

    with open(json_file, "w") as f:
        json.dump(json_data, f, indent=2, ensure_ascii=False)
    return


def create_dotenv_file(required_variable_names: list, dotenv=".env"):
    """
    Create a .env file with the required environment variables.

    Args:
        required_variable_names (list): A list of variable names to include in the .env file.
        dotenv (str, optional): The name of the .env file to create (default is ".env").

    Returns:
        bool: True if the .env file was created, False if it was skipped.
    """
    if os.path.exists(dotenv):
        logger.info(
            "File {} already exists. Would you like to overwrite it? [Y/n]".format(
                dotenv
            )
        )
        answer = input()
        if answer.lower() == "n":
            logger.info("Skipping .env file creation...")
            return False

    logger.info("Creating .env file...")
    with open(dotenv, "w") as f:
        for var_name in required_variable_names:
            logger.info(f"Enter value for {var_name}:")
            value = input()
            f.write(f"{var_name}={value}\n")

    return True
