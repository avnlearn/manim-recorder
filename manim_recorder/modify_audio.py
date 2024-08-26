import os
import sox
import uuid
from mutagen.mp3 import MP3
from pydub.utils import mediainfo
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


def get_duration(path : str) -> float:
    # Create a Path object
    file_path = Path(path)
    
    # Use match-case to check the file extension
    match file_path.suffix.lower():
        case '.mp3':
            audio = MP3(path)
            return audio.info.length
        case '.m4a':
            audio = mediainfo(path)
            return float(audio['duration'])
        case '.wav':
            with wave.open(str(path), "rb") as wav_file:
                return wav_file.getnframes() / wav_file.getframerate()
        case _:
            return False
    
