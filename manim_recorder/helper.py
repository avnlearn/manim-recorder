"""
helper for manim-recorder
"""

import json
import os
import textwrap
from manim import logger


def msg_box(msg, indent=1, width=None, title=None):
    """Print message-box with optional title."""
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
    """Append data to json file"""
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
                final_audio = "{}/{}".format(
                    os.path.dirname(json_file), final_audio)
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
    """Create a .env file with the required variables"""
    if os.path.exists(dotenv):
        logger.info(
            "File {} already exists. Would you like to overwrite it? [Y/n]".format(dotenv))
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
