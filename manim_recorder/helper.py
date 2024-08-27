import importlib
import json
import re
import os
import sys
from typing import Union
import pip
import textwrap
from pydub import AudioSegment
from pathlib import Path
from manim import logger


def chunks(lst: list, n: int):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i: i + n]


def wav2mp3(wav_path, mp3_path=None, remove_wav=True, bitrate="312k"):
    """Convert wav file to mp3 file"""

    if mp3_path is None:
        mp3_path = Path(wav_path).with_suffix(".mp3")

    # Convert to mp3
    AudioSegment.from_wav(wav_path).export(
        mp3_path, format="mp3", bitrate=bitrate)

    if remove_wav:
        # Remove the .wav file
        os.remove(wav_path)
    logger.info(f"Saved {mp3_path}")
    return


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


def detect_leading_silence(sound, silence_threshold=-20.0, chunk_size=10):
    """
    sound is a pydub.AudioSegment
    silence_threshold in dB
    chunk_size in ms

    iterate over chunks until you find the first one with sound
    """
    trim_ms = 0  # ms

    assert chunk_size > 0  # to avoid infinite loop
    while sound[
        trim_ms: trim_ms + chunk_size
    ].dBFS < silence_threshold and trim_ms < len(sound):
        trim_ms += chunk_size

    return trim_ms


def trim_silence(
    sound: AudioSegment,
    silence_threshold=-40.0,
    chunk_size=5,
    buffer_start=200,
    buffer_end=200,
) -> AudioSegment:
    start_trim = detect_leading_silence(sound, silence_threshold, chunk_size)
    end_trim = detect_leading_silence(
        sound.reverse(), silence_threshold, chunk_size)

    # Remove buffer_len milliseconds from start_trim and end_trim
    start_trim = max(0, start_trim - buffer_start)
    end_trim = max(0, end_trim - buffer_end)

    duration = len(sound)
    trimmed_sound = sound[start_trim: duration - end_trim]
    return trimmed_sound


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
