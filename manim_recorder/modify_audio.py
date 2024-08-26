import os
import sox
import uuid
from mutagen.mp3 import MP3
import wave

from pathlib import Path


def adjust_speed(input_path: str, output_path: str, tempo: float) -> None:
    same_destination = False
    if input_path == output_path:
        same_destination = True
        path_, ext = os.path.splitext(input_path)
        output_path = path_ + str(uuid.uuid1()) + ext

    tfm = sox.Transformer()
    tfm.tempo(tempo)
    tfm.build(input_filepath=input_path, output_filepath=output_path)
    if same_destination:
        os.rename(output_path, input_path)


def get_duration(path: str) -> float:
    
    with wave.open(str(path), "rb") as wav_file:
        return wav_file.getnframes() / wav_file.getframerate()

    # with wave.open(str(path), 'rb') as wav_file:
    #     frames = wav_file.getnframes()  # Total number of frames
    #     rate = wav_file.getframerate()  # Frame rate (samples per second)
    #     duration = frames / float(rate)  # Duration in seconds
    # print("Wav :", duration)
    # return duration
    # audio = MP3(path)
    # return audio.info.length
    # return sox.file_info.duration(path)
